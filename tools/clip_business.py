#!/usr/bin/env python3
"""Local, zero-API-cost clip operations. No downloads, uploads, or posting.

All commercial claims are operator-entered, not inferred from views.
Use creator-supplied/local footage only, with documented permission.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

HOME = Path(os.environ.get("CLIP_OPS_HOME", Path.home() / ".local/share/openshorts-ops"))


def read(name):
    path = HOME / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def write(name, items):
    HOME.mkdir(parents=True, exist_ok=True)
    path = HOME / f"{name}.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def append(name, item):
    entries = read(name)
    entries.append(item)
    write(name, entries)
    return item


def find(name, item_id):
    for item in read(name):
        if item["id"] == item_id:
            return item
    raise ValueError(f"Unknown {name} ID: {item_id}")


def uid():
    return uuid.uuid4().hex[:10]


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def source_add(args):
    source = Path(args.file).expanduser().resolve(strict=True)
    if not source.is_file():
        raise ValueError("Source must be a local media file")
    if not args.permission_ref.strip():
        raise ValueError("Written permission reference is required; a public video URL is not permission")
    entry = append("sources", {"id": uid(), "file": str(source), "creator": args.creator,
                               "permission_ref": args.permission_ref, "scope": args.scope, "date": stamp()})
    print(f"SOURCE {entry['id']} added. Operator must ensure publisher/game rights also permit intended use.")


def campaign_add(args):
    if not args.url.startswith("https://"):
        raise ValueError("Campaign must have an HTTPS link to its official brief")
    if args.rate < 0 or args.cap < 0:
        raise ValueError("Rates and caps cannot be negative")
    if args.rules_verified and not args.rules_ref.strip():
        raise ValueError("Verified campaign rules need an evidence reference")
    entry = append("campaigns", {"id": uid(), "name": args.name, "url": args.url,
                                 "rate_usd_per_1k": args.rate, "cap_usd": args.cap,
                                 "payout_eligibility": args.payout, "rules_verified": args.rules_verified,
                                 "rules_ref": args.rules_ref, "date": stamp()})
    print(f"CAMPAIGN {entry['id']} added ({entry['payout_eligibility']}; this is not a payment promise)")


def clip_render(args):
    source = find("sources", args.source)
    if args.seconds < 7 or args.seconds > 60 or args.start < 0:
        raise ValueError("Use a 7–60-second clip and a non-negative start time")
    if args.campaign:
        camp = find("campaigns", args.campaign)
        if camp["payout_eligibility"] != "verified" or not camp["rules_verified"]:
            raise ValueError("Campaign blocked: first verify Nigerian payout eligibility and full rules")
    if source["scope"] not in ("clip-service", "social-commercial", "campaign"):
        raise ValueError("Source permission does not cover clip production")
    if args.campaign and source["scope"] not in ("social-commercial", "campaign"):
        raise ValueError("Source does not grant commercial posting/campaign use")
    src = Path(source["file"])
    if not src.exists():
        raise ValueError(f"Source media missing: {src}")
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg is not installed; run: brew install ffmpeg")
    clip_id = uid()
    dest = HOME / "renders" / f"{clip_id}.mp4"
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Letterbox instead of hard-cropping gameplay; title/captions can be added in OpenShorts.
    filt = ("scale=1080:1920:force_original_aspect_ratio=decrease:force_divisible_by=2,"
            "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=0x10151b,fps=30,format=yuv420p")
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-ss", str(args.start),
           "-i", str(src), "-t", str(args.seconds), "-vf", filt,
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "aac",
           "-b:a", "160k", "-movflags", "+faststart", str(dest)]
    subprocess.run(cmd, check=True)
    entry = append("clips", {"id": clip_id, "source_id": source["id"],
                             "campaign_id": args.campaign, "path": str(dest), "title": args.title,
                             "platform": args.platform, "created": stamp(), "posted": False})
    sidecar = dest.with_suffix(".json")
    sidecar.write_text(json.dumps({"id": clip_id, "title": args.title, "platform": args.platform,
                                   "source_creator": source["creator"], "permission_ref": source["permission_ref"],
                                   "campaign_id": args.campaign, "publish": "MANUAL REVIEW ONLY"}, indent=2),
                       encoding="utf-8")
    print(f"RENDER {entry['id']} -> {dest}\nManual review: rights, captions, attribution, claims, music, and platform rules.")


def lead_add(args):
    if args.offer < 0:
        raise ValueError("Lead offer cannot be negative")
    entry = append("leads", {"id": uid(), "handle": args.handle, "platform": args.platform,
                              "offer_ngn": args.offer, "status": "prospect", "contacted": False,
                              "date": stamp()})
    print(f"LEAD {entry['id']} added — no message was sent")


def payment_record(args):
    if args.amount <= 0 or not args.reference:
        raise ValueError("Use a positive amount and payment reference")
    if args.status not in ("pending", "received"):
        raise ValueError("Status must be pending or received")
    if any(p["reference"] == args.reference and p["currency"] == args.currency for p in read("payments")):
        raise ValueError("Duplicate payment reference: update the existing record instead")
    append("payments", {"id": uid(), "party": args.party, "amount": args.amount,
                        "currency": args.currency, "reference": args.reference,
                        "status": args.status, "date": stamp()})
    print(f"PAYMENT {args.status}: {args.currency} {args.amount:,.2f}")


def report(_args):
    leads = read("leads")
    clips = read("clips")
    pays = read("payments")
    camps = read("campaigns")
    print(f"Sources: {len(read('sources'))} | Campaigns: {len(camps)} | Clips: {len(clips)} | Leads: {len(leads)}")
    for currency in ("NGN", "USD"):
        received = sum(p["amount"] for p in pays if p["currency"] == currency and p["status"] == "received")
        pending = sum(p["amount"] for p in pays if p["currency"] == currency and p["status"] == "pending")
        print(f"{currency} RECEIVED: {received:,.2f} | PENDING (not earned cash): {pending:,.2f}")
    print("Views and estimates are NOT counted as received money.")


def build_parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("source-add")
    s.add_argument("--file", required=True); s.add_argument("--creator", required=True)
    s.add_argument("--permission-ref", required=True, help="Written creator authorization URL or file reference")
    s.add_argument("--scope", choices=["clip-service", "social-commercial", "campaign"], required=True)
    s.set_defaults(run=source_add)
    s = sub.add_parser("campaign-add")
    s.add_argument("--name", required=True); s.add_argument("--url", required=True)
    s.add_argument("--rate", type=float, required=True); s.add_argument("--cap", type=float, default=0)
    s.add_argument("--payout", choices=["unknown", "blocked", "verified"], default="unknown")
    s.add_argument("--rules-ref", default=""); s.add_argument("--rules-verified", action="store_true")
    s.set_defaults(run=campaign_add)
    s = sub.add_parser("render")
    s.add_argument("--source", required=True); s.add_argument("--start", type=float, required=True)
    s.add_argument("--seconds", type=float, required=True); s.add_argument("--title", required=True)
    s.add_argument("--platform", choices=["tiktok", "instagram", "youtube", "x"], required=True)
    s.add_argument("--campaign"); s.set_defaults(run=clip_render)
    s = sub.add_parser("lead-add")
    s.add_argument("--handle", required=True); s.add_argument("--platform", required=True)
    s.add_argument("--offer", type=float, required=True); s.set_defaults(run=lead_add)
    s = sub.add_parser("payment-record")
    s.add_argument("--party", required=True); s.add_argument("--amount", type=float, required=True)
    s.add_argument("--currency", choices=["NGN", "USD"], required=True)
    s.add_argument("--reference", required=True); s.add_argument("--status", choices=["pending", "received"], required=True)
    s.set_defaults(run=payment_record)
    s = sub.add_parser("report"); s.set_defaults(run=report)
    return p


def main():
    args = build_parser().parse_args()
    try:
        args.run(args)
    except (ValueError, FileNotFoundError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
