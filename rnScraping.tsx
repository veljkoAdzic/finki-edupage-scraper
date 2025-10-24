import React, { useState, useRef } from "react";
import { View, Text, Button, ActivityIndicator } from "react-native";
import { WebView } from "react-native-webview";

export default function TimetableFetcher() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const webviewRef = useRef(null);

  // JS that will run inside the WebView (browser context).
  // It:
  // 1) Performs the first POST to getTTViewerData
  // 2) Extracts default_num (X)
  // 3) Performs the second POST with X
  // 4) Posts the final payload (or error) to React Native via window.ReactNativeWebView.postMessage
  const injectedJS = `
    (function() {
      async function run() {
        try {
          // small helper to perform a POST and parse JSON or text
          async function postJson(url, bodyObj) {
            const res = await fetch(url, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "Accept": "application/json, text/javascript, */*; q=0.01"
                // You can add Referer here if necessary:
                // "Referer": "https://finki.edupage.org/timetable/"
              },
              body: JSON.stringify(bodyObj),
              credentials: "same-origin"
            });
            // server may respond with JSON or JS; try text then JSON.parse
            const text = await res.text();
            try { return JSON.parse(text); } catch(e) { return text; }
          }

          // 1) getTTViewerData
          const viewerResp = await postJson("/timetable/server/ttviewer.js?__func=getTTViewerData", { __args: [null, 2025], __gsh: "00000000" });
          // validate
          if (!viewerResp || !viewerResp.r || !viewerResp.r.regular) {
            window.ReactNativeWebView.postMessage(JSON.stringify({ ok: false, error: "Invalid viewer response", viewerResp }));
            return;
          }

          const X = viewerResp.r.regular.default_num;
          // 2) regularttGetData with X
          const regResp = await postJson("/timetable/server/regulartt.js?__func=regularttGetData", { __args: [null, X], __gsh: "00000000" });

          // send results back
          window.ReactNativeWebView.postMessage(JSON.stringify({ ok: true, X: X, viewerResp, regResp }));
        } catch (err) {
          window.ReactNativeWebView.postMessage(JSON.stringify({ ok: false, error: err && err.message ? err.message : String(err) }));
        }
      }

      // Delay slightly to ensure cookies/session are set and page JS has loaded
      setTimeout(run, 500);
    })();
    true; // note: required to signal success on Android WebView
  `;

  return (
    <View style={{ flex: 1 }}>
      {!data ? (
        <>
          <Text style={{ padding: 12 }}>Press "Fetch" to load timetable data</Text>
          <Button
            title={loading ? "Fetching..." : "Fetch"}
            onPress={() => {
              setLoading(true);
              // load the timetable page in webview and run the injected script
              // (we render the WebView below which auto-loads the URL and runs injectedJS)
            }}
          />
          <View style={{ height: 0, width: 0, opacity: 0 }}>
            {/* Hidden WebView — it loads the site; injectedJS will postMessage results */}
            <WebView
              ref={webviewRef}
              source={{ uri: "https://finki.edupage.org/timetable/" }}
              injectedJavaScript={injectedJS}
              onMessage={(event) => {
                try {
                  const msg = JSON.parse(event.nativeEvent.data);
                  if (msg.ok) {
                    setData(msg);
                  } else {
                    console.warn("Timetable fetch error:", msg.error, msg);
                    setData({ error: msg.error, raw: msg });
                  }
                } catch (e) {
                  console.warn("Could not parse message from WebView:", e, event.nativeEvent.data);
                  setData({ error: "parse_error", raw: event.nativeEvent.data });
                } finally {
                  setLoading(false);
                }
              }}
              javaScriptEnabled
              originWhitelist={["*"]}
              // some sites require setting these
              // mixedContentMode="always"
              // domStorageEnabled
            />
          </View>
          {loading && <ActivityIndicator />}
        </>
      ) : (
        <View style={{ padding: 12 }}>
          <Text>Result:</Text>
          <Text selectable>{JSON.stringify(data, null, 2)}</Text>
          <Button title="Clear" onPress={() => setData(null)} />
        </View>
      )}
    </View>
  );
}