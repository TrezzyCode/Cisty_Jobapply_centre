"""Capture Cisty's real PySide UI with a completely isolated fictional dataset."""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import sys
from pathlib import Path

PROMO_DIR = Path(__file__).resolve().parent
APP_DIR = PROMO_DIR.parent
RUNTIME_DIR = PROMO_DIR / "capture_runtime"
DATA_DIR = RUNTIME_DIR / "IT Internship Auto Apply"
CAPTURE_DIR = PROMO_DIR / "public" / "captures"


def prepare_runtime() -> None:
    if RUNTIME_DIR.exists():
        shutil.rmtree(RUNTIME_DIR)
    DATA_DIR.mkdir(parents=True)
    CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    # Existing files prevent main.py's legacy migration from touching real user data.
    (DATA_DIR / "internship_applications.db").touch()
    settings = {
        "student_name": "Alex Tan",
        "course": "Diploma in Information Technology",
        "internship_period": "January – May 2027",
        "phone": "+60 12-000 0000",
        "sender_email": "alex.tan@example.test",
        "resume_path": "",
        "credentials_path": "",
        "geoapify_api_key": "",
        "profile_avatar_path": "",
        "profile_ready": True,
    }
    (DATA_DIR / "settings.json").write_text(json.dumps(settings, indent=2), encoding="utf-8")
    os.environ["LOCALAPPDATA"] = str(RUNTIME_DIR)
    # Use the native Windows font stack. The offscreen plugin cannot resolve
    # Segoe UI reliably in packaged/sandboxed sessions and produces tofu boxes.
    os.environ["QT_QPA_PLATFORM"] = "windows"
    os.environ["CISTY_REDUCE_MOTION"] = "1"


def seed_database() -> None:
    from main import db

    companies = [
        ("Aster Loop Systems", "Technology", "Bukit Bintang", "Kuala Lumpur", "MRT Kajang Line", "Bukit Bintang", 420, 6, "internships@asterloop.example", 1, "Ready to apply"),
        ("Banyan Cloud Studio", "Technology", "Kuala Lumpur", "Kuala Lumpur", "MRT Putrajaya Line", "Persiaran KLCC", 680, 9, "people@banyancloud.example", 1, "Draft ready"),
        ("Cedar Data Works", "Technology", "Petaling Jaya", "Selangor", "LRT Kelana Jaya Line", "Asia Jaya", 510, 7, "careers@cedardata.example", 1, "Not applied"),
        ("Emberline Creative", "Arts / Entertainment", "Kuala Lumpur", "Kuala Lumpur", "KL Monorail", "Raja Chulan", 360, 5, "hello@emberline.example", 1, "Applied"),
        ("Kitewell Analytics", "Technology", "Damansara", "Selangor", "MRT Kajang Line", "TTDI", 890, 12, "talent@kitewell.example", 1, "No response"),
        ("Luma Transit Lab", "Engineering", "Kuala Lumpur", "Kuala Lumpur", "MRT Putrajaya Line", "Conlay", 290, 4, "intern@lumatransit.example", 1, "Interview"),
        ("Meridian Byte Labs", "Technology", "Kuala Lumpur", "Kuala Lumpur", "MRT Putrajaya Line", "Ampang Park", 240, 3, "careers@meridianbyte.example", 1, "Replied"),
        ("Northstar Product House", "Technology", "Kepong", "Kuala Lumpur", "MRT Putrajaya Line", "Metro Prima", 760, 10, "join@northstarproduct.example", 1, "Not applied"),
        ("Orbit Grove Solutions", "Technology", "Seri Kembangan", "Selangor", "MRT Putrajaya Line", "Seri Kembangan", 610, 8, "team@orbitgrove.example", 1, "Ready to apply"),
        ("Pebble Stack Labs", "Technology", "Bangsar", "Kuala Lumpur", "LRT Kelana Jaya Line", "Bangsar", 330, 5, "jobs@pebblestack.example", 1, "Draft ready"),
        ("Sunroom Commerce", "E-commerce", "Kuala Lumpur", "Kuala Lumpur", "LRT Kelana Jaya Line", "KLCC", 940, 13, "campus@sunroom.example", 1, "Not applied"),
        ("Willowframe Media", "Arts / Entertainment", "Imbi", "Kuala Lumpur", "KL Monorail", "Imbi", 190, 3, "studio@willowframe.example", 1, "Applied"),
    ]
    con = db()
    con.execute("DELETE FROM system_messages")
    con.execute("DELETE FROM system_threads")
    con.execute("DELETE FROM companies")
    for index, row in enumerate(companies):
        name, industry, city, state, line, station, meters, minutes, email, verified, status = row
        con.execute(
            """INSERT INTO companies (
                name, website, address, postcode, city, state, country, industry,
                hr_email, email_source, email_verified, email_verified_at,
                station, station_line, walk_distance_meters, walk_minutes,
                route_verified, station_calculation_source, station_calculated_at,
                status, last_sent, last_contact
            ) VALUES (?, ?, ?, ?, ?, ?, 'Malaysia', ?, ?, 'Imported Excel', ?,
                '2026-11-20 10:00', ?, ?, ?, ?, 1, 'Geoapify + saved result',
                '2026-11-20 10:06', ?, '2026-11-18 09:30', '2026-11-21 15:42')""",
            (
                name, f"https://{name.lower().replace(' ', '')}.example", f"{18 + index} Jalan Harmoni",
                f"50{index:03d}", city, state, industry, email, verified, station, line,
                meters, minutes, status,
            ),
        )
    company_id = con.execute("SELECT id FROM companies WHERE name='Meridian Byte Labs'").fetchone()[0]
    con.execute(
        "INSERT INTO system_threads(company_id,gmail_thread_id,recipient,initial_message_id,last_synced_at) VALUES(?,?,?,?,?)",
        (company_id, "demo-thread-meridian", "careers@meridianbyte.example", "demo-outbound-1", "2026-11-21 15:42"),
    )
    messages = [
        ("demo-outbound-1", "outbound", "Alex Tan <alex.tan@example.test>", "Meridian Byte Labs <careers@meridianbyte.example>", "Application for Software Internship", "Hello Meridian Byte Labs team,\n\nI am applying for your software internship and have attached my resume for review.\n\nKind regards,\nAlex", "18 Nov 2026, 09:30", 1794975000000),
        ("demo-inbound-1", "inbound", "Meridian Byte Labs <careers@meridianbyte.example>", "Alex Tan <alex.tan@example.test>", "Re: Application for Software Internship", "Hi Alex,\n\nThank you for your application. We would like to invite you to a short online interview next Tuesday.\n\nBest,\nMeridian People Team", "21 Nov 2026, 15:42", 1795261320000),
    ]
    for message_id, direction, sender, recipient, subject, body, sent_at, internal_date in messages:
        con.execute(
            """INSERT INTO system_messages(
                gmail_message_id,company_id,gmail_thread_id,direction,sender,recipient,
                subject,body,sent_at,internal_date
            ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (message_id, company_id, "demo-thread-meridian", direction, sender, recipient, subject, body, sent_at, internal_date),
        )
    con.commit()
    con.close()


def save_widget(widget, name: str) -> None:
    from PySide6.QtCore import QCoreApplication

    for _ in range(8):
        QCoreApplication.processEvents()
    pixmap = widget.grab()
    if not pixmap.save(str(CAPTURE_DIR / name), "PNG"):
        raise RuntimeError(f"Could not save {name}")


def main() -> int:
    prepare_runtime()
    sys.path.insert(0, str(APP_DIR))
    seed_database()

    from PySide6.QtWidgets import QApplication
    from qt_main import MainWindow

    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.resize(1920, 1080)
    window.move(-2400, -1400)
    window.show()
    app.processEvents()
    window.gmail_sync_status.setText("Synced just now • 8 applications • 1 reply")

    # Applications: full list with the hero company selected.
    for row in range(window.table.rowCount()):
        if window.table.item(row, 0).text() == "Meridian Byte Labs":
            window.table.selectRow(row)
            break
    app.processEvents()
    save_widget(window, "applications-all.png")

    # A real filtered state used at the end of the type-and-filter shot.
    window.industry_filter.setCurrentText("Technology")
    window.region_filter.setCurrentText("Kuala Lumpur / Selangor")
    window.line_filter.setCurrentText("MRT Putrajaya Line")
    window.search.setText("Meridian")
    app.processEvents()
    if window.table.rowCount():
        window.table.selectRow(0)
    save_widget(window, "applications-filtered.png")

    # The saved station result and the tracked system-only Gmail thread.
    window.search.clear()
    window.industry_filter.setCurrentText("All industries")
    window.region_filter.setCurrentText("All regions")
    window.line_filter.setCurrentText("All transit lines")
    window.refresh()
    for row in range(window.table.rowCount()):
        if window.table.item(row, 0).text() == "Meridian Byte Labs":
            window.table.selectRow(row)
            break
    window.inspector_tabs.setCurrentIndex(0)
    save_widget(window, "station-detail.png")
    window.inspector_tabs.setCurrentIndex(2)
    save_widget(window, "conversation.png")

    layout = {
        "size": {"width": 1920, "height": 1080},
        "search": {"x": 1215, "y": 22, "width": 520, "height": 42},
        "filters": {"x": 210, "y": 122, "width": 1696, "height": 124},
        "table": {"x": 210, "y": 256, "width": 1176, "height": 812},
        "inspector": {"x": 1398, "y": 256, "width": 508, "height": 812},
    }
    (CAPTURE_DIR / "layout.json").write_text(json.dumps(layout, indent=2), encoding="utf-8")
    window.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
