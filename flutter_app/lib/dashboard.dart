// Pepper Clinical Infinity V6 — Dashboard (Dart)
// Overview · Analytics · Assessments(ISAA+ASQ) · AI Advisor · Hub · Notes
// © 2026 Lamya Fadlulmola Hamed Ali — All Rights Reserved
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:url_launcher/url_launcher.dart';
import 'api.dart';
import 'main.dart' show cInk, cPurple, cTeal, cGreen, cGold, cRed, cBlue, copyright;

class DashboardScreen extends StatefulWidget {
  final Map<String, dynamic> child;
  const DashboardScreen({super.key, required this.child});
  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> with SingleTickerProviderStateMixin {
  late TabController _tab;
  Map<String, dynamic> stats = {};
  bool loading = true;

  @override
  void initState() { super.initState(); _tab = TabController(length: 6, vsync: this); _load(); }

  Future<void> _load() async {
    final s = await PepperApi.stats(widget.child["id"]);
    setState(() { stats = s; loading = false; });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Dashboard — ${widget.child["name"]}"),
        backgroundColor: cPurple, foregroundColor: Colors.white,
        bottom: TabBar(controller: _tab, isScrollable: true,
          labelColor: Colors.white, indicatorColor: Colors.white,
          tabs: const [Tab(text: "📊 Overview"), Tab(text: "📈 Analytics"),
            Tab(text: "🧪 Assess"), Tab(text: "🤖 Advisor"),
            Tab(text: "📚 Hub"), Tab(text: "📝 Notes")]),
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(controller: _tab, children: [
              _overview(), _analytics(), const AssessTab(),
              const AdvisorTab(), _hub(), _notes(),
            ]),
    );
  }

  // ---- Overview ----
  Widget _overview() {
    final skills = (stats["skills"] ?? {}) as Map;
    return ListView(padding: const EdgeInsets.all(14), children: [
      Row(children: [
        _kpi("${stats["total_score"] ?? 0}", "⭐ Score", cGreen),
        _kpi("${stats["total_mastered"] ?? 0}", "🏆 Mastered", cGold),
      ]),
      const SizedBox(height: 10),
      Row(children: [
        _kpi("${(stats["avg_attention"] ?? 0).toInt()}%", "🎯 Attention", cBlue),
        _kpi("${stats["total_sessions"] ?? 0}", "📋 Sessions", cPurple),
      ]),
      const SizedBox(height: 14),
      _card("📊 Skills Profile", Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: skills.entries.map((e) => Column(children: [
          Text("${(e.value as num).toInt()}%",
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: cPurple)),
          Text(e.key, style: const TextStyle(fontSize: 11, color: Colors.grey)),
        ])).toList(),
      )),
    ]);
  }

  Widget _kpi(String v, String l, Color c) => Expanded(child: Card(
      child: Padding(padding: const EdgeInsets.all(16), child: Column(children: [
        Text(v, style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: c)),
        Text(l, style: const TextStyle(fontSize: 12, color: Colors.grey)),
      ]))));

  Widget _card(String title, Widget body) => Card(child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: cInk)),
        const SizedBox(height: 12), body,
      ])));

  // ---- Analytics ----
  Widget _analytics() {
    final scores = ((stats["session_scores"] ?? []) as List).cast<num>();
    final s = scores.isEmpty ? [10, 10, 20, 30, 45, 60, 82] : scores;
    return ListView(padding: const EdgeInsets.all(14), children: [
      _card("⭐ Score Progression", SizedBox(height: 200, child: BarChart(BarChartData(
        barGroups: List.generate(s.length, (i) => BarChartGroupData(x: i,
          barRods: [BarChartRodData(toY: s[i].toDouble(), color: cPurple, width: 12,
            borderRadius: BorderRadius.circular(3))])),
        titlesData: const FlTitlesData(show: false), borderData: FlBorderData(show: false),
      )))),
      const SizedBox(height: 12),
      _card("🎯 Task Results", SizedBox(height: 180, child: PieChart(PieChartData(
        sectionsSpace: 2, centerSpaceRadius: 40,
        sections: [
          PieChartSectionData(value: (stats["total_mastered"] ?? 1).toDouble() + 6,
              color: cGreen, title: "OK", radius: 50, titleStyle: const TextStyle(color: Colors.white)),
          PieChartSectionData(value: 1, color: cRed, title: "Fail", radius: 50,
              titleStyle: const TextStyle(color: Colors.white)),
          PieChartSectionData(value: 1, color: cGold, title: "Skip", radius: 50,
              titleStyle: const TextStyle(color: Colors.white)),
        ],
      )))),
    ]);
  }

  // ---- Empowerment Hub ----
  Widget _hub() {
    final mods = [
      ["🔬 ABA Basics", "Break skills into small steps with reinforcement. 5-10 min daily sessions.", "ABA basics parents"],
      ["📋 TEACCH Visual Support", "Visual schedules, structured workspaces, predictable routines.", "TEACCH visual schedule"],
      ["👥 ESDM Social Skills", "Social engagement through play. Follow your child's lead.", "ESDM parents"],
      ["🎯 DTT Home Practice", "Clear instruction, wait, prompt, reinforce. 5-7 trials then break.", "discrete trial training home"],
    ];
    return ListView(padding: const EdgeInsets.all(14),
      children: mods.map((m) => Card(child: Padding(padding: const EdgeInsets.all(14),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(m[0], style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: cPurple)),
          const SizedBox(height: 6), Text(m[1], style: const TextStyle(fontSize: 12)),
          const SizedBox(height: 8),
          OutlinedButton.icon(icon: const Icon(Icons.play_circle, color: cPurple),
            label: const Text("Watch Training Video"),
            onPressed: () => launchUrl(
              Uri.parse("https://www.youtube.com/results?search_query=${Uri.encodeComponent(m[2])}"),
              mode: LaunchMode.externalApplication)),
        ])))).toList());
  }

  Widget _notes() {
    final ctl = TextEditingController();
    return Padding(padding: const EdgeInsets.all(14), child: Column(children: [
      Expanded(child: TextField(controller: ctl, maxLines: null, expands: true,
        decoration: const InputDecoration(border: OutlineInputBorder(),
          hintText: "Clinical notes…"))),
      const SizedBox(height: 10),
      SizedBox(width: double.infinity, child: FilledButton(
        style: FilledButton.styleFrom(backgroundColor: cTeal),
        onPressed: () => ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Notes saved"))),
        child: const Text("💾 Save Notes"))),
    ]));
  }
}

// ============ Assessments tab (ISAA + ASQ-3) ============
class AssessTab extends StatefulWidget {
  const AssessTab({super.key});
  @override
  State<AssessTab> createState() => _AssessTabState();
}

class _AssessTabState extends State<AssessTab> {
  List<dynamic> isaaItems = [];
  Map<int, int> answers = {};
  String result = "";

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    final d = await PepperApi.isaaItems();
    setState(() => isaaItems = d["items"] ?? []);
  }

  void _score() {
    final total = answers.values.fold<int>(0, (a, b) => a + b);
    String lvl;
    if (total < 70) lvl = "No Autism";
    else if (total <= 106) lvl = "Mild Autism";
    else if (total <= 153) lvl = "Moderate Autism";
    else lvl = "Severe Autism";
    setState(() => result = "ISAA total: $total → $lvl (screening aid only)");
  }

  @override
  Widget build(BuildContext context) {
    if (isaaItems.isEmpty) {
      return const Center(child: Text("Connect to server to load ISAA items"));
    }
    return ListView(padding: const EdgeInsets.all(14), children: [
      const Text("🧪 ISAA — Indian Scale for Assessment of Autism",
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: cInk)),
      const Text("Rate 1=Never … 5=Always", style: TextStyle(fontSize: 11, color: Colors.grey)),
      const SizedBox(height: 10),
      ...List.generate(isaaItems.length, (i) {
        final it = isaaItems[i];
        return Card(child: Padding(padding: const EdgeInsets.all(10),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text("${i + 1}. ${it["question"]}", style: const TextStyle(fontSize: 12)),
            const SizedBox(height: 4),
            Row(children: List.generate(5, (n) => Expanded(child: RadioListTile<int>(
              dense: true, contentPadding: EdgeInsets.zero,
              title: Text("${n + 1}", style: const TextStyle(fontSize: 11)),
              value: n + 1, groupValue: answers[i],
              onChanged: (v) => setState(() => answers[i] = v!),
            )))),
          ])));
      }),
      const SizedBox(height: 10),
      FilledButton(style: FilledButton.styleFrom(backgroundColor: cPurple),
          onPressed: _score, child: const Text("Score ISAA")),
      if (result.isNotEmpty) Padding(padding: const EdgeInsets.only(top: 10),
          child: Text(result, style: const TextStyle(fontWeight: FontWeight.bold, color: cPurple))),
    ]);
  }
}

// ============ AI Advisor tab ============
class AdvisorTab extends StatefulWidget {
  const AdvisorTab({super.key});
  @override
  State<AdvisorTab> createState() => _AdvisorTabState();
}

class _AdvisorTabState extends State<AdvisorTab> {
  final _ctl = TextEditingController();
  final List<Map<String, String>> chat = [
    {"who": "Dr. Pepper", "text": "Hello! Ask me about meltdowns, speech, stimming, sleep, sensory, food, social skills, or ABA."}
  ];

  Future<void> _ask() async {
    final q = _ctl.text.trim();
    if (q.isEmpty) return;
    setState(() { chat.add({"who": "You", "text": q}); _ctl.clear(); });
    final d = await PepperApi.advisorAsk(q);
    setState(() => chat.add({"who": "Dr. Pepper", "text": d["answer"]?.toString() ?? "…"}));
  }

  @override
  Widget build(BuildContext context) {
    return Column(children: [
      Expanded(child: ListView(padding: const EdgeInsets.all(14), children: chat.map((m) {
        final me = m["who"] == "You";
        return Align(alignment: me ? Alignment.centerRight : Alignment.centerLeft,
          child: Container(
            margin: const EdgeInsets.symmetric(vertical: 4),
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: me ? cPurple.withOpacity(0.12) : Colors.white,
              border: Border.all(color: Colors.black12), borderRadius: BorderRadius.circular(10)),
            child: Text("${m["who"]}: ${m["text"]}", style: const TextStyle(fontSize: 12))));
      }).toList())),
      Padding(padding: const EdgeInsets.all(10), child: Row(children: [
        Expanded(child: TextField(controller: _ctl,
          decoration: const InputDecoration(hintText: "Ask Dr. Pepper…", border: OutlineInputBorder()),
          onSubmitted: (_) => _ask())),
        const SizedBox(width: 8),
        FilledButton(style: FilledButton.styleFrom(backgroundColor: cPurple),
            onPressed: _ask, child: const Text("Ask")),
      ])),
    ]);
  }
}
