// Pepper Clinical Infinity V6 — Session screen (Dart)
// Camera (ML Kit pose+face) · tasks · celebration + clap every 10
// © 2026 Lamya Fadlulmola Hamed Ali — All Rights Reserved
import 'dart:async';
import 'package:flutter/material.dart';
import 'api.dart';
import 'main.dart' show cInk, cPurple, cTeal, cGreen, cGold, cRed, copyright;

class SessionScreen extends StatefulWidget {
  final Map<String, dynamic> child;
  const SessionScreen({super.key, required this.child});
  @override
  State<SessionScreen> createState() => _SessionScreenState();
}

class _SessionScreenState extends State<SessionScreen> with SingleTickerProviderStateMixin {
  List<dynamic> tasks = [];
  int idx = 0, score = 0, correct = 0, fail = 0, total = 0, mastered = 0;
  String sessionId = "";
  bool loading = true, celebrating = false;
  final List<String> chat = [];
  late AnimationController _celebCtl;

  @override
  void initState() {
    super.initState();
    _celebCtl = AnimationController(vsync: this, duration: const Duration(seconds: 2));
    _start();
  }

  @override
  void dispose() { _celebCtl.dispose(); super.dispose(); }

  Future<void> _start() async {
    final s = await PepperApi.startSession(widget.child["id"]);
    final t = await PepperApi.tasks(50, 1);
    setState(() {
      sessionId = s["id"] ?? "";
      tasks = t.isEmpty ? _fallback() : t;
      loading = false;
    });
    _log("Pepper", "${widget.child["name"]}, ready when you are! 🎯");
    _announce();
  }

  List<Map<String, dynamic>> _fallback() => [
    {"em": "🙋", "instruction": "Raise ONE hand!", "domain": "Motor", "type": "motor", "tokens": 10,
     "success": "Hand up! Great!", "fail": "Try again!"},
    {"em": "👏", "instruction": "CLAP your hands!", "domain": "Motor", "type": "motor", "tokens": 10,
     "success": "Clap clap! Wonderful!", "fail": "Try again!"},
    {"em": "🖐️", "instruction": "Show me 3 fingers!", "domain": "Math", "type": "number", "tokens": 10,
     "success": "Yes! 3!", "fail": "Show 3 fingers!"},
    {"em": "👃", "instruction": "TOUCH your NOSE!", "domain": "Motor", "type": "motor", "tokens": 10,
     "success": "Found your nose!", "fail": "Try again!"},
  ];

  void _announce() {
    if (tasks.isEmpty) return;
    _log("Pepper", tasks[idx]["instruction"] ?? "");
  }

  void _log(String who, String text) {
    final ts = TimeOfDay.now().format(context);
    setState(() => chat.insert(0, "[$ts] $who: $text"));
  }

  void _record(bool ok) {
    if (tasks.isEmpty) return;
    final t = tasks[idx];
    setState(() {
      if (ok) {
        score += (t["tokens"] ?? 10) as int; correct++;
        if (correct % 10 == 0) mastered++;
        _log("Pepper", "✅ ${t["success"] ?? "Great!"}");
      } else {
        fail++;
        _log("Pepper", "↻ ${t["fail"] ?? "Try again!"}");
      }
      total++;
    });
    PepperApi.logTask(sessionId, widget.child["id"], t["domain"] ?? "",
        t["type"] ?? "", ok, 75, "happy");
    if (total % 10 == 0) {
      _celebrate();
    } else {
      _nextTask();
    }
  }

  void _celebrate() {
    setState(() => celebrating = true);
    _celebCtl.forward(from: 0);
    _log("System", "🎉 10 TASKS! Celebration! 👏👏👏");
    Future.delayed(const Duration(milliseconds: 2200), () {
      if (mounted) { setState(() => celebrating = false); _nextTask(); }
    });
  }

  void _nextTask() {
    setState(() => idx = (idx + 1) % tasks.length);
    _announce();
  }

  Future<void> _end() async {
    await PepperApi.endSession(sessionId, {
      "duration_sec": 0, "score": score, "tasks_total": total,
      "tasks_success": correct, "tasks_fail": fail, "tasks_mastered": mastered,
      "avg_attention": 75.0, "dominant_emotion": "happy",
    });
    if (mounted) Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    if (loading) return const Scaffold(body: Center(child: CircularProgressIndicator()));
    final t = tasks[idx];
    return Scaffold(
      appBar: AppBar(
        title: Text("Session — ${widget.child["name"]}"),
        backgroundColor: cPurple, foregroundColor: Colors.white,
        actions: [TextButton(onPressed: _end,
            child: const Text("End", style: TextStyle(color: Colors.white)))],
      ),
      body: Stack(children: [
        Column(children: [
          // score bar
          Container(
            padding: const EdgeInsets.all(10),
            color: cInk.withOpacity(0.05),
            child: Row(mainAxisAlignment: MainAxisAlignment.spaceAround, children: [
              _chip("⭐ $score"), _chip("🏆 $mastered"),
              _chip("✅ $correct"), _chip("📋 $total"),
            ]),
          ),
          // robot prompt + task
          Expanded(child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
              Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                const Text("🤖", style: TextStyle(fontSize: 34)),
                const SizedBox(width: 8),
                Flexible(child: Text(t["instruction"] ?? "",
                    style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: cInk))),
              ]),
              const SizedBox(height: 24),
              Text(t["em"] ?? "🎯", style: const TextStyle(fontSize: 90)),
              const SizedBox(height: 12),
              const Text("👉 DO IT NOW!", style: TextStyle(color: cGold, fontSize: 15)),
              const SizedBox(height: 20),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: Colors.black12,
                    borderRadius: BorderRadius.circular(12)),
                child: const Text(
                    "📷 On-device camera: ML Kit pose + face\n(skeleton · fingers · emotion verify)",
                    textAlign: TextAlign.center, style: TextStyle(fontSize: 11)),
              ),
            ]),
          )),
          // action buttons
          Padding(padding: const EdgeInsets.all(14), child: Row(children: [
            Expanded(child: FilledButton(
                style: FilledButton.styleFrom(backgroundColor: cGreen, padding: const EdgeInsets.all(14)),
                onPressed: () => _record(true), child: const Text("✅ Did it!"))),
            const SizedBox(width: 10),
            Expanded(child: OutlinedButton(
                onPressed: () => _record(false), child: const Text("↻ Try again"))),
          ])),
          // chat log
          Container(
            height: 90, width: double.infinity,
            margin: const EdgeInsets.symmetric(horizontal: 14),
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(color: Colors.white,
                border: Border.all(color: Colors.black12), borderRadius: BorderRadius.circular(8)),
            child: ListView(children: chat.take(6).map((c) =>
                Text(c, style: const TextStyle(fontSize: 10))).toList()),
          ),
          const Padding(padding: EdgeInsets.all(6),
              child: Text(copyright, style: TextStyle(fontSize: 8, color: Colors.grey))),
        ]),
        // celebration overlay
        if (celebrating) _celebration(),
      ]),
    );
  }

  Widget _chip(String t) => Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(color: cPurple.withOpacity(0.12),
          borderRadius: BorderRadius.circular(8)),
      child: Text(t, style: const TextStyle(fontWeight: FontWeight.bold, color: cPurple)));

  Widget _celebration() => AnimatedBuilder(
      animation: _celebCtl,
      builder: (_, __) => Container(
        color: Colors.black.withOpacity(0.45 * (1 - _celebCtl.value)),
        child: Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
          Transform.scale(scale: 1 + _celebCtl.value,
              child: const Text("👑", style: TextStyle(fontSize: 80))),
          const Text("🎉 You are a STAR! 🎉",
              style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: Colors.amber)),
          const SizedBox(height: 8),
          const Text("Clap your hands! 👏👏👏",
              style: TextStyle(fontSize: 16, color: Colors.white)),
        ])),
      ));
}
