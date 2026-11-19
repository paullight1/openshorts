"""Safe offline regression tests. No network, publishing, or real video downloads."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("clip_business", ROOT / "tools" / "clip_business.py")
ops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ops)


class ClipOpsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.old_home = ops.HOME
        ops.HOME = Path(self.tmp.name) / "data"
        self.addCleanup(setattr, ops, "HOME", self.old_home)
        self.sample = Path(self.tmp.name) / "creator supplied.mp4"
        self.sample.write_bytes(b"test only")

    def source(self, **overrides):
        opts = dict(file=str(self.sample), creator="Test Creator", permission_ref="signed-email-001", scope="social-commercial")
        opts.update(overrides)
        ops.source_add(SimpleNamespace(**opts))
        return ops.read("sources")[-1]["id"]

    def campaign(self, **overrides):
        opts = dict(name="Test Campaign", url="https://example.com/campaign", rate=1.0,
                    cap=100, payout="verified", rules_verified=True, rules_ref="email-002")
        opts.update(overrides)
        ops.campaign_add(SimpleNamespace(**opts))
        return ops.read("campaigns")[-1]["id"]

    def test_public_video_url_is_not_permission(self):
        with self.assertRaises(ValueError):
            self.source(permission_ref="")
        self.assertEqual(ops.read("sources"), [])

    def test_unverified_payout_blocks_campaign(self):
        sid = self.source()
        cid = self.campaign(payout="unknown")
        with self.assertRaisesRegex(ValueError, "verify Nigerian payout"):
            ops.clip_render(SimpleNamespace(source=sid, campaign=cid, seconds=20, start=0,
                                           title="Test", platform="youtube"))

    def test_out_of_scope_source_blocks_campaign(self):
        sid = self.source(scope="clip-service")
        cid = self.campaign()
        with self.assertRaisesRegex(ValueError, "commercial"):
            ops.clip_render(SimpleNamespace(source=sid, campaign=cid, seconds=20, start=0,
                                           title="Test", platform="youtube"))

    @patch.object(ops.shutil, "which", return_value="/usr/bin/ffmpeg")
    @patch.object(ops.subprocess, "run")
    def test_render_only_local_with_manual_review(self, run_mock, which_mock):
        sid = self.source()
        ops.clip_render(SimpleNamespace(source=sid, campaign=None, seconds=20, start=4,
                                        title="Original analysis", platform="youtube"))
        self.assertEqual(len(ops.read("clips")), 1)
        args = run_mock.call_args.args[0]
        self.assertEqual(args[0], "/usr/bin/ffmpeg")
        self.assertIn(str(self.sample), args)
        self.assertTrue(run_mock.call_args.kwargs["check"])
        self.assertEqual(ops.read("clips")[0]["posted"], False)

    def test_received_cash_never_counts_pending(self):
        ops.payment_record(SimpleNamespace(party="Client A", amount=5000, currency="NGN", reference="bank-ref-1", status="pending"))
        ops.payment_record(SimpleNamespace(party="Client B", amount=7000, currency="NGN", reference="bank-ref-2", status="received"))
        rows = ops.read("payments")
        self.assertEqual(sum(p["amount"] for p in rows if p["status"] == "received"), 7000)

    def test_no_network_or_publishing_code(self):
        src = (ROOT / "tools" / "clip_business.py").read_text()
        self.assertNotIn("requests.post", src)
        self.assertNotIn("yt_dlp", src)


if __name__ == "__main__":
    unittest.main()
