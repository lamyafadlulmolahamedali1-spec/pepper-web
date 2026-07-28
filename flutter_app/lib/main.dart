// Pepper Clinical Infinity V6 — Flutter Mobile App
// © 2026 Lamya Fadlulmola Hamed Ali — All Rights Reserved
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'api.dart';
import 'session.dart';
import 'dashboard.dart';

// ---- Theme colors (match the desktop app) ----
const cInk = Color(0xFF2D2B69);
const cPurple = Color(0xFF7C3AED);
const cPurple2 = Color(0xFF6D28D9);
const cTeal = Color(0xFF0D9488);
const cGreen = Color(0xFF10B981);
const cGold = Color(0xFFF59E0B);
const cRed = Color(0xFFEF4444);
const cBlue = Color(0xFF3B82F6);
const cBg = Color(0xFFF4F6FB);
const cCard = Colors.white;
const copyright = "© 2026 Lamya Fadlulmola Hamed Ali — Pepper Clinical Infinity V6";

void main() => runApp(const PepperApp());

class PepperApp extends StatelessWidget {
  const PepperApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: "Pepper Clinical V6",
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        scaffoldBackgroundColor: cBg,
        colorScheme: ColorScheme.fromSeed(seedColor: cPurple),
        useMaterial3: true,
        fontFamily: 'Roboto',
      ),
      home: const AuthScreen(),
    );
  }
}

// ============ AUTH (Login / Trial / Subscribe) ============
class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key});
  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> with SingleTickerProviderStateMixin {
  late TabController _tab;
  final _le = TextEditingController(), _lp = TextEditingController();
  final _tn = TextEditingController(), _te = TextEditingController(), _tc = TextEditingController();
  int _tage = 6;
  final _se = TextEditingController();
  int _plan = 0;
  String _msg = "";
  bool _busy = false;

  @override
  void initState() { super.initState(); _tab = TabController(length: 3, vsync: this); }

  Future<void> _login() async {
    setState(() { _busy = true; _msg = ""; });
    final d = await PepperApi.login(_le.text.trim(), _lp.text.trim());
    setState(() => _busy = false);
    if (d["access_token"] != null && mounted) {
      Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const HomeScreen()));
    } else { setState(() => _msg = d["detail"]?.toString() ?? "Login failed"); }
  }

  Future<void> _trial() async {
    setState(() { _busy = true; _msg = ""; });
    final d = await PepperApi.trial(_tn.text.trim(), _te.text.trim(),
        _tc.text.trim().isEmpty ? "Child" : _tc.text.trim(), _tage);
    setState(() => _busy = false);
    final pin = d["pin"];
    if (pin != null) {
      setState(() => _msg = "Trial created! Your PIN: $pin (save it, use Login tab)");
    } else { setState(() => _msg = d["detail"]?.toString() ?? "Could not create trial"); }
  }

  Future<void> _subscribe() async {
    const plans = ["individual_monthly", "individual_yearly",
                   "institution_monthly", "institution_yearly"];
    final url = await PepperApi.checkout(plans[_plan], _se.text.trim());
    if (url != null) {
      await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
    } else { setState(() => _msg = "Connect to server to enable Stripe checkout"); }
  }

  InputDecoration _dec(String h) => InputDecoration(
      labelText: h, border: const OutlineInputBorder(),
      contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 14));

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 440),
            child: Card(
              elevation: 4,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(mainAxisSize: MainAxisSize.min, children: [
                  const Text("🤖", style: TextStyle(fontSize: 50)),
                  const Text("Pepper Clinical Infinity V6",
                      style: TextStyle(fontSize: 19, fontWeight: FontWeight.bold, color: cInk)),
                  const SizedBox(height: 14),
                  TabBar(controller: _tab, labelColor: cPurple, indicatorColor: cPurple,
                      tabs: const [Tab(text: "Login"), Tab(text: "Trial"), Tab(text: "Subscribe")]),
                  SizedBox(
                    height: 300,
                    child: TabBarView(controller: _tab, children: [
                      // Login
                      Padding(padding: const EdgeInsets.only(top: 16), child: Column(children: [
                        TextField(controller: _le, decoration: _dec("Email")),
                        const SizedBox(height: 10),
                        TextField(controller: _lp, obscureText: true, decoration: _dec("PIN")),
                        const SizedBox(height: 14),
                        _btn("Login", cPurple, _busy ? null : _login),
                      ])),
                      // Trial
                      Padding(padding: const EdgeInsets.only(top: 16), child: Column(children: [
                        TextField(controller: _tn, decoration: _dec("Your name")),
                        const SizedBox(height: 8),
                        TextField(controller: _te, decoration: _dec("Email")),
                        const SizedBox(height: 8),
                        TextField(controller: _tc, decoration: _dec("Child name")),
                        const SizedBox(height: 14),
                        _btn("Start 15-Day Free Trial", cTeal, _busy ? null : _trial),
                      ])),
                      // Subscribe
                      Padding(padding: const EdgeInsets.only(top: 16), child: Column(children: [
                        TextField(controller: _se, decoration: _dec("Email")),
                        const SizedBox(height: 10),
                        DropdownButtonFormField<int>(
                          value: _plan,
                          decoration: _dec("Plan"),
                          items: const [
                            DropdownMenuItem(value: 0, child: Text("Individual — Monthly £49")),
                            DropdownMenuItem(value: 1, child: Text("Individual — Yearly £399")),
                            DropdownMenuItem(value: 2, child: Text("Institution 10 — Monthly £399")),
                            DropdownMenuItem(value: 3, child: Text("Institution 10 — Yearly £3990")),
                          ],
                          onChanged: (v) => setState(() => _plan = v ?? 0),
                        ),
                        const SizedBox(height: 14),
                        _btn("Subscribe with Stripe 💳", cPurple2, _busy ? null : _subscribe),
                      ])),
                    ]),
                  ),
                  if (_msg.isNotEmpty)
                    Padding(padding: const EdgeInsets.only(top: 8),
                        child: Text(_msg, style: const TextStyle(color: cTeal, fontSize: 12),
                            textAlign: TextAlign.center)),
                  const SizedBox(height: 8),
                  const Text(copyright, style: TextStyle(fontSize: 8, color: Colors.grey)),
                ]),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _btn(String t, Color c, VoidCallback? onTap) => SizedBox(
      width: double.infinity,
      child: FilledButton(
        style: FilledButton.styleFrom(backgroundColor: c, padding: const EdgeInsets.all(14)),
        onPressed: onTap, child: Text(t)));
}

// ============ HOME (children list) ============
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<dynamic> kids = [];
  bool loading = true;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    final c = await PepperApi.children();
    setState(() { kids = c; loading = false; });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Pepper Clinical V6"),
        backgroundColor: cPurple, foregroundColor: Colors.white,
        actions: [IconButton(icon: const Icon(Icons.logout), onPressed: () async {
          await PepperApi.logout();
          if (mounted) Navigator.pushReplacement(context,
              MaterialPageRoute(builder: (_) => const AuthScreen()));
        })],
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : kids.isEmpty
              ? const Center(child: Text("No children yet."))
              : ListView(padding: const EdgeInsets.all(14), children: kids.map((c) {
                  return Card(
                    margin: const EdgeInsets.only(bottom: 10),
                    child: ListTile(
                      leading: CircleAvatar(backgroundColor: cPurple,
                          child: Text(c["name"][0], style: const TextStyle(color: Colors.white))),
                      title: Text(c["name"], style: const TextStyle(fontWeight: FontWeight.bold)),
                      subtitle: Text("Age ${c["age"]} · ${c["total_sessions"]} sessions"),
                      trailing: Row(mainAxisSize: MainAxisSize.min, children: [
                        IconButton(icon: const Icon(Icons.play_circle, color: cPurple),
                            onPressed: () => Navigator.push(context, MaterialPageRoute(
                                builder: (_) => SessionScreen(child: c)))),
                        IconButton(icon: const Icon(Icons.bar_chart, color: cTeal),
                            onPressed: () => Navigator.push(context, MaterialPageRoute(
                                builder: (_) => DashboardScreen(child: c)))),
                      ]),
                    ),
                  );
                }).toList()),
      bottomNavigationBar: const Padding(padding: EdgeInsets.all(6),
          child: Text(copyright, textAlign: TextAlign.center,
              style: TextStyle(fontSize: 9, color: Colors.grey))),
    );
  }
}
