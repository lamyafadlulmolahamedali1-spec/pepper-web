// Pepper Clinical Infinity V6 — Secure API Client (Dart)
// © 2026 Lamya Fadlulmola Hamed Ali — All Rights Reserved
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class PepperApi {
  static String baseUrl = "http://10.0.2.2:8000"; // emulator->localhost; change for device

  static const _store = FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
  );

  static Future<void> _saveTokens(String a, String r) async {
    await _store.write(key: "access", value: a);
    await _store.write(key: "refresh", value: r);
  }

  static Future<String?> get token => _store.read(key: "access");

  static Future<Map<String, String>> _headers({bool auth = true}) async {
    final h = {"Content-Type": "application/json"};
    if (auth) {
      final t = await token;
      if (t != null) h["Authorization"] = "Bearer $t";
    }
    return h;
  }

  // ---- Auth ----
  static Future<Map<String, dynamic>> trial(
      String name, String email, String childName, int age) async {
    final r = await http.post(Uri.parse("$baseUrl/api/auth/trial"),
        headers: await _headers(auth: false),
        body: jsonEncode({
          "full_name": name, "email": email,
          "child_name": childName, "child_age": age
        }));
    return _dec(r);
  }

  static Future<Map<String, dynamic>> login(String email, String pin) async {
    final r = await http.post(Uri.parse("$baseUrl/api/auth/login"),
        headers: await _headers(auth: false),
        body: jsonEncode({"email": email, "pin": pin}));
    final d = _dec(r);
    if (d["access_token"] != null) {
      await _saveTokens(d["access_token"], d["refresh_token"] ?? "");
    }
    return d;
  }

  static Future<void> logout() async => _store.deleteAll();

  // ---- Children ----
  static Future<List<dynamic>> children() async {
    final r = await http.get(Uri.parse("$baseUrl/api/children"),
        headers: await _headers());
    try { return jsonDecode(r.body) as List<dynamic>; } catch (_) { return []; }
  }

  // ---- Sessions ----
  static Future<Map<String, dynamic>> startSession(String childId) async {
    final r = await http.post(Uri.parse("$baseUrl/api/sessions/start"),
        headers: await _headers(),
        body: jsonEncode({"child_id": childId, "protocol": "ABA-DTT"}));
    return _dec(r);
  }

  static Future<List<dynamic>> tasks(int count, int level) async {
    final r = await http.post(Uri.parse("$baseUrl/api/sessions/tasks/generate"),
        headers: await _headers(),
        body: jsonEncode({"count": count, "level": level}));
    return _dec(r)["tasks"] ?? [];
  }

  static Future<void> logTask(String sid, String cid, String domain, String type,
      bool ok, double attn, String emo) async {
    await http.post(Uri.parse("$baseUrl/api/sessions/log-task"),
        headers: await _headers(),
        body: jsonEncode({"session_id": sid, "child_id": cid, "domain": domain,
          "task_type": type, "success": ok, "attention": attn, "emotion": emo}));
  }

  static Future<void> endSession(String sid, Map<String, dynamic> s) async {
    await http.post(Uri.parse("$baseUrl/api/sessions/end"),
        headers: await _headers(),
        body: jsonEncode({"session_id": sid, ...s}));
  }

  static Future<Map<String, dynamic>> stats(String cid) async {
    final r = await http.get(Uri.parse("$baseUrl/api/sessions/stats/$cid"),
        headers: await _headers());
    return _dec(r);
  }

  // ---- Clinical ----
  static Future<Map<String, dynamic>> isaaItems() async {
    final r = await http.get(Uri.parse("$baseUrl/api/clinical/isaa/items"),
        headers: await _headers(auth: false));
    return _dec(r);
  }

  static Future<Map<String, dynamic>> advisorAsk(String q) async {
    final r = await http.post(Uri.parse("$baseUrl/api/clinical/advisor/ask"),
        headers: await _headers(auth: false),
        body: jsonEncode({"question": q}));
    return _dec(r);
  }

  // ---- Billing ----
  static Future<String?> checkout(String plan, String email) async {
    final r = await http.post(Uri.parse("$baseUrl/api/billing/checkout"),
        headers: await _headers(auth: false),
        body: jsonEncode({"plan": plan, "email": email}));
    return _dec(r)["checkout_url"];
  }

  static Map<String, dynamic> _dec(http.Response r) {
    try { return jsonDecode(r.body) as Map<String, dynamic>; }
    catch (_) { return {"error": "bad response", "status": r.statusCode}; }
  }
}
