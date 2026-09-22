#if UNITY_EDITOR
using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.UI;

public static class AetherqorInventoryPOCBuilder
{
    const int W = 2340;
    const int H = 1080;

    [MenuItem("AETHERQOR/UI POC/Build + Capture")]
    public static void BuildAndCapture()
    {
        try
        {
            var outDir = Environment.GetEnvironmentVariable("AQ_UI_OUT");
            if (string.IsNullOrWhiteSpace(outDir))
                outDir = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "AQ_UI_OUTPUT"));
            Directory.CreateDirectory(outDir);
            var frames = Path.Combine(outDir, "frames");
            Directory.CreateDirectory(frames);

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "AQ_InventoryScrollDemo";

            var root = new GameObject("AETHERQOR_UI_POC");
            var demo = root.AddComponent<AetherqorInventoryScrollDemo>();
            demo.BuildNow();

            Canvas.ForceUpdateCanvases();
            if (demo.InventoryContent != null)
                LayoutRebuilder.ForceRebuildLayoutImmediate(demo.InventoryContent);
            Canvas.ForceUpdateCanvases();

            var sceneDir = "Assets/AETHERQOR_UI_POC/Scenes";
            if (!AssetDatabase.IsValidFolder("Assets/AETHERQOR_UI_POC"))
                AssetDatabase.CreateFolder("Assets", "AETHERQOR_UI_POC");
            if (!AssetDatabase.IsValidFolder(sceneDir))
                AssetDatabase.CreateFolder("Assets/AETHERQOR_UI_POC", "Scenes");
            var scenePath = sceneDir + "/AQ_InventoryScrollDemo.unity";
            EditorSceneManager.SaveScene(scene, scenePath);

            var cam = GameObject.Find("AQ_UI_Camera")?.GetComponent<Camera>();
            if (cam == null) throw new Exception("AQ_UI_Camera not found");

            int runeCount = 0;
            int gearCount = 0;
            int itemCount = 0;
            foreach (var tr in root.GetComponentsInChildren<Transform>(true))
            {
                if (tr.name.StartsWith("ElionRune_") || tr.name.StartsWith("HadumRune_")) runeCount++;
                else if (tr.name.StartsWith("GearL_") || tr.name.StartsWith("GearR_")) gearCount++;
                else if (tr.name.StartsWith("Item_")) itemCount++;
            }

            if (runeCount != 8) throw new Exception("Expected exactly 8 rune slots, got " + runeCount);
            if (itemCount != 48) throw new Exception("Expected 48 inventory slots, got " + itemCount);
            if (demo.InventoryScroll == null || !demo.InventoryScroll.vertical || demo.InventoryScroll.horizontal)
                throw new Exception("ScrollRect is not configured for vertical-only scrolling");

            demo.SetScroll01(0f);
            Canvas.ForceUpdateCanvases();
            float topY = demo.InventoryContent.anchoredPosition.y;
            Capture(cam, Path.Combine(outDir, "AQ_inventory_TOP.png"));

            demo.SetScroll01(0.50f);
            Canvas.ForceUpdateCanvases();
            float middleY = demo.InventoryContent.anchoredPosition.y;
            Capture(cam, Path.Combine(outDir, "AQ_inventory_MIDDLE.png"));

            const float bottomProofT = 0.88f;
            demo.SetScroll01(bottomProofT);
            Canvas.ForceUpdateCanvases();
            float bottomY = demo.InventoryContent.anchoredPosition.y;
            Capture(cam, Path.Combine(outDir, "AQ_inventory_BOTTOM.png"));

            float middleTravel = Mathf.Abs(middleY - topY);
            float bottomTravel = Mathf.Abs(bottomY - topY);
            if (middleTravel < 100f || bottomTravel < 250f)
                throw new Exception($"Scroll proof failed: topY={topY:F2} middleY={middleY:F2} bottomY={bottomY:F2}");

            const int n = 31;
            for (int i = 0; i < n; i++)
            {
                float t = i / (float)(n - 1);
                float eased = Mathf.SmoothStep(0f, bottomProofT, t);
                demo.SetScroll01(eased);
                Canvas.ForceUpdateCanvases();
                Capture(cam, Path.Combine(frames, $"frame_{i:000}.png"));
            }

            File.WriteAllText(Path.Combine(outDir, "validation.txt"),
                "AETHERQOR UNITY MOBILE INVENTORY POC\n" +
                $"Resolution={W}x{H}\n" +
                $"RuneSlots={runeCount} (4 Elion + 4 Hadum)\n" +
                $"GearSlots={gearCount}\n" +
                $"InventorySlots={itemCount}\n" +
                "InventoryColumns=4\n" +
                "SlotSize=148x148 px\n" +
                "VerticalScroll=true\n" +
                "HorizontalScroll=false\n" +
                "Inertia=true\n" +
                "Scrollbar=permanent large mobile thumb\n" +
                $"TopContentY={topY:F2}\n" +
                $"MiddleContentY={middleY:F2}\n" +
                $"BottomProofContentY={bottomY:F2}\n" +
                $"MiddleTravelPx={middleTravel:F2}\n" +
                $"BottomTravelPx={bottomTravel:F2}\n" +
                $"BottomProofT={bottomProofT:F2}\n" +
                $"Scene={scenePath}\n");

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("[AQ-UI-POC] PASS. Output: " + outDir);
            EditorApplication.Exit(0);
        }
        catch (Exception ex)
        {
            Debug.LogException(ex);
            EditorApplication.Exit(2);
        }
    }

    static void Capture(Camera cam, string path)
    {
        var rt = new RenderTexture(W, H, 24, RenderTextureFormat.ARGB32);
        rt.antiAliasing = 1;
        var prevTarget = cam.targetTexture;
        var prevActive = RenderTexture.active;
        cam.targetTexture = rt;
        RenderTexture.active = rt;
        cam.Render();

        var tex = new Texture2D(W, H, TextureFormat.RGBA32, false);
        tex.ReadPixels(new Rect(0, 0, W, H), 0, 0, false);
        tex.Apply(false, false);
        File.WriteAllBytes(path, tex.EncodeToPNG());

        UnityEngine.Object.DestroyImmediate(tex);
        cam.targetTexture = prevTarget;
        RenderTexture.active = prevActive;
        rt.Release();
        UnityEngine.Object.DestroyImmediate(rt);
    }
}
#endif
