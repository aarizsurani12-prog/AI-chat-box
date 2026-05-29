const https = require("https");

const SYSTEM_PROMPT = `You are an assistant for a digital printing service. Use ONLY the following facts to answer user questions:

Address: Shop No. G-3, Shivam Plaza, K. K Marg, near Jyoti Sport Stores, Nani Daman, Marwad 396210. (Plus Code: CR8M+H8).

Ratings: We have a 4.8-star rating from 19 reviews.

Business Hours: Monday to Saturday, 10 AM to 6 PM. Sunday closed.

Our Services:
- Luxury Wedding Cards & Invitations
- Offset & Digital Printing
- Posters & Banners
- Visiting Cards
- T-Shirt & Bag Printing
- All Types of Stationery
- Pamphlet & Handbill
- Hotel Menu Cards
- PVC ID Cards
- Rubber Stamp
- Brochures & Catalog
- Flex Printing
- Labels & Stickers
- Calendars & Lottery
- 3D & 2D Printing

Important Rules:
- Whenever mentioning numbers or dates, always write them in digits (like 1, 2, 3) instead of spelling them out.
- Do not make up any information.
- If a question is not related to our shop, politely respond that you can only assist with questions about our printing services, location, hours, or ratings.`;

function getCurrentTimeIST() {
  const now = new Date();
  const istOffset = 5.5 * 60 * 60 * 1000;
  const ist = new Date(now.getTime() + istOffset);
  const days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
  const months = ["January","February","March","April","May","June","July","August","September","October","November","December"];
  const day = days[ist.getUTCDay()];
  const date = String(ist.getUTCDate()).padStart(2, "0");
  const month = months[ist.getUTCMonth()];
  const year = ist.getUTCFullYear();
  let hours = ist.getUTCHours();
  const minutes = String(ist.getUTCMinutes()).padStart(2, "0");
  const ampm = hours >= 12 ? "PM" : "AM";
  hours = hours % 12 || 12;
  return `Current date/time (IST): ${day}, ${date} ${month} ${year}, ${hours}:${minutes} ${ampm}. Use this to answer questions like 'Are you open now?' or 'What time do you close today?'.`;
}

function askGemini(apiKey, messages) {
  return new Promise((resolve, reject) => {
    const contents = messages.map((m) => ({
      role: m.role === "assistant" ? "model" : "user",
      parts: [{ text: m.content }],
    }));

    const payload = JSON.stringify({
      system_instruction: {
        parts: [{ text: `${SYSTEM_PROMPT}\n\n${getCurrentTimeIST()}` }],
      },
      contents,
    });

    const options = {
      hostname: "generativelanguage.googleapis.com",
      path: `/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(payload),
      },
    };

    const req = https.request(options, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        try {
          const json = JSON.parse(data);
          if (json.error) return reject(new Error(json.error.message || JSON.stringify(json.error)));
          resolve(json.candidates[0].content.parts[0].text);
        } catch (e) {
          reject(new Error("Failed to parse Gemini response: " + data));
        }
      });
    });

    req.on("error", reject);
    req.write(payload);
    req.end();
  });
}

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.status(200).end();
    return;
  }

  if (req.method !== "POST") {
    res.status(405).json({ error: "Method not allowed" });
    return;
  }

  const apiKey = process.env.GOOGLE_API_KEY;
  if (!apiKey) {
    res.status(500).json({ error: "GOOGLE_API_KEY not set" });
    return;
  }

  try {
    const messages = req.body?.messages || [];
    const reply = await askGemini(apiKey, messages);
    res.status(200).json({ text: reply });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
};
