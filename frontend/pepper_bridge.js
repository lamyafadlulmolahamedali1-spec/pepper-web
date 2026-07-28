const PEPPER_API = "http://localhost:5055";

async function peppSpeak(on) {
  return fetch(`${PEPPER_API}/pepper/speak`, {
    method: "POST", headers: {"Content-Type":"application/json"},
    body: JSON.stringify({on})
  }).catch(()=>{});
}
async function peppWave(duration=2.2) {
  return fetch(`${PEPPER_API}/pepper/wave`, {
    method: "POST", headers: {"Content-Type":"application/json"},
    body: JSON.stringify({duration})
  }).catch(()=>{});
}
async function peppClap(duration=2.0) {
  return fetch(`${PEPPER_API}/pepper/clap`, {
    method: "POST", headers: {"Content-Type":"application/json"},
    body: JSON.stringify({duration})
  }).catch(()=>{});
}
async function peppLook(yaw=0, pitch=0, hold=2.5) {
  return fetch(`${PEPPER_API}/pepper/look`, {
    method: "POST", headers: {"Content-Type":"application/json"},
    body: JSON.stringify({yaw, pitch, hold})
  }).catch(()=>{});
}

// اربطيها مع أحداث Pepper Clinical مثلاً:
// عند بدء TTS: peppSpeak(true)
// عند انتهاء TTS: peppSpeak(false)
// عند فتح تمرين جديد: peppWave()
// عند إجابة صحيحة: peppClap()
