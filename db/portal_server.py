"""
Local API + static file server so the sponsor portal writes gifts to SQLite.

Usage:
  python db/portal_server.py --open
  # or double-click OPEN_DEMO.bat
  Open http://127.0.0.1:8765/

Endpoints:
  GET  /api/health
  GET  /api/freshness
  GET  /api/ops
  GET  /api/student/<id>/arrears
  GET  /api/receipts
  POST /api/payments   JSON: {student_id, amount, term_labels[], sponsor?}
"""

from __future__ import annotations

import json
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

DB_DIR = Path(__file__).resolve().parent
ROOT = DB_DIR.parent
if str(DB_DIR) not in sys.path:
    sys.path.insert(0, str(DB_DIR))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from record_payment import (  # noqa: E402
    OverpaymentError,
    StaleBalanceError,
    apply_payment,
    connect,
    list_receipts,
    payment_receipt,
    term_arrears_summary,
)
from freshness import freshness_report  # noqa: E402
from ops_metrics import log_settlement_attempt, ops_snapshot  # noqa: E402

HOST = '127.0.0.1'
PORT = 8765


class PortalHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _cors(self) -> None:
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _json(self, code: int, payload: dict | list) -> None:
        body = json.dumps(payload).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/health':
            self._json(200, {'ok': True, 'db': 'elimu_match.db'})
            return

        if path == '/api/freshness':
            self._json(200, freshness_report())
            return

        if path == '/api/ops':
            self._json(200, ops_snapshot())
            return

        if path.startswith('/api/student/') and path.endswith('/arrears'):
            try:
                student_id = int(path.split('/')[3])
            except (IndexError, ValueError):
                self._json(400, {'error': 'Invalid student id'})
                return
            conn = connect()
            terms = term_arrears_summary(conn, student_id)
            conn.close()
            total = sum(t['outstanding'] for t in terms)
            self._json(200, {'student_id': student_id, 'terms': terms, 'amount': total})
            return

        if path == '/api/receipts':
            conn = connect()
            receipts = list_receipts(conn, limit=50)
            conn.close()
            self._json(200, {'receipts': receipts})
            return

        if path.startswith('/api/'):
            self._json(404, {'error': 'Not found'})
            return

        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != '/api/payments':
            self._json(404, {'error': 'Not found'})
            return

        length = int(self.headers.get('Content-Length', 0))
        raw = self.rfile.read(length) if length else b'{}'
        try:
            data = json.loads(raw.decode('utf-8'))
        except json.JSONDecodeError:
            self._json(400, {'error': 'Invalid JSON'})
            return

        try:
            student_id = int(data['student_id'])
            amount = int(data['amount'])
            term_labels = data.get('term_labels') or []
            if not isinstance(term_labels, list) or not term_labels:
                raise ValueError('term_labels must be a non-empty list')
            term_labels = [str(t) for t in term_labels]
            sponsor = str(data.get('sponsor') or 'Portal Sponsor')
            if amount <= 0:
                raise ValueError('amount must be positive')
            expected = data.get('expected_outstanding')
            expected_outstanding = int(expected) if expected is not None else None
        except (KeyError, TypeError, ValueError) as exc:
            self._json(400, {'error': str(exc)})
            return

        conn = connect()
        try:
            payment_id = apply_payment(
                conn,
                student_id=student_id,
                amount=amount,
                term_labels=term_labels,
                sponsor_name=sponsor,
                source='portal_server.py',
                expected_outstanding=expected_outstanding,
            )
            receipt = payment_receipt(conn, payment_id)
            receipt['policy'] = {
                'ledger_authoritative': True,
                'overpayment': 'rejected',
                'stale_screen': 'rejected_until_refresh',
            }
            self._json(200, {'ok': True, 'receipt': receipt})
        except OverpaymentError as exc:
            terms = term_arrears_summary(conn, student_id)
            avail = sum(t['outstanding'] for t in terms)
            log_settlement_attempt(
                conn,
                code='overpayment',
                student_id=student_id,
                amount_kes=amount,
                expected_outstanding=expected_outstanding,
                available_outstanding=avail,
                detail=str(exc),
            )
            self._json(409, {
                'error': str(exc),
                'code': 'overpayment',
                'requested': exc.requested,
                'available': exc.available,
                'terms': terms,
                'amount': avail,
            })
        except StaleBalanceError as exc:
            terms = term_arrears_summary(conn, student_id)
            selected = [t for t in terms if t['term_label'] in term_labels]
            avail = sum(t['outstanding'] for t in terms)
            log_settlement_attempt(
                conn,
                code='stale_balance',
                student_id=student_id,
                amount_kes=amount,
                expected_outstanding=exc.expected,
                available_outstanding=exc.actual,
                detail=str(exc),
            )
            self._json(409, {
                'error': str(exc),
                'code': 'stale_balance',
                'expected': exc.expected,
                'actual': exc.actual,
                'terms': terms,
                'amount': avail,
                'selected_outstanding': sum(t['outstanding'] for t in selected),
            })
        except Exception as exc:  # noqa: BLE001
            conn.rollback()
            self._json(400, {'error': str(exc)})
        finally:
            conn.close()

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f'[portal] {self.address_string()} - {fmt % args}\n')


def main() -> None:
    import argparse
    import socket
    import webbrowser

    parser = argparse.ArgumentParser(description='ElimuMatch portal + static demo server')
    parser.add_argument('--open', action='store_true', help='Open home page in the browser')
    parser.add_argument('--port', type=int, default=PORT, help=f'Port (default {PORT})')
    args = parser.parse_args()
    port = args.port

    # Fail clearly if the port is already taken (common mid-demo issue).
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        probe.bind((HOST, port))
    except OSError:
        print(f'Port {port} is already in use.')
        print(f'If a previous demo is still running, open http://{HOST}:{port}/')
        print(f'Or stop that process and try again, or use: python db/portal_server.py --port {port + 1} --open')
        sys.exit(1)
    finally:
        probe.close()

    server = ThreadingHTTPServer((HOST, port), PortalHandler)
    home = f'http://{HOST}:{port}/'
    print('=' * 60)
    print('ELIMUMATCH DEMO SERVER')
    print('=' * 60)
    print(f'Home:      {home}')
    print(f'Portal:    http://{HOST}:{port}/sponsor_portal.html')
    print(f'Ops:       http://{HOST}:{port}/ops_dashboard.html')
    print(f'Analytics: http://{HOST}:{port}/dashboard.html')
    print(f'API:       http://{HOST}:{port}/api/health')
    print('Gifts write to SQLite (db/elimu_match.db)')
    print('Ctrl+C to stop')
    print('=' * 60)
    if args.open:
        webbrowser.open(home)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')
        server.server_close()


if __name__ == '__main__':
    main()
