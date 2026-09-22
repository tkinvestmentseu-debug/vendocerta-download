#if UNITY_EDITOR
using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.UI;

public static class AetherqorInventoryPOCBuilderV2
{
    const int W = 2340;
    const int H = 1080;
    const string SkinPath = "Assets/AETHERQOR_UI_POC/Textures/AQ_inventory_skin.png";

    public static void BuildAndCapture()
    {
        try
        {
            string outDir = Environment.GetEnvironmentVariable("AQ_UI_OUT");
            if (string.IsNullOrWhiteSpace(outDir))
                outDir = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "AQ_UI_OUTPUT"));
            Directory.CreateDirectory(outDir);
            string frames = Path.Combine(outDir, "frames");
            Directory.CreateDirectory(frames);

            AssetDatabase.ImportAsset(SkinPath, ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
            var skin = AssetDatabase.LoadAssetAtPath<Texture2D>(SkinPath);
            if (skin == null) throw new Exception("Dark fantasy skin missing: " + SkinPath);
            if (skin.width != 1846 || skin.height != 852)
                throw new Exception($"Unexpected skin resolution {skin.width}x{skin.height}; expected 1846x852");

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "AQ_InventoryScrollDemo_DarkFantasy";

            var root = new GameObject("AETHERQOR_UI_DARK_FANTASY_POC");
            var demo = root.AddComponent<AetherqorInventoryScrollDemoV2>();
            demo.BuildNow();
            demo.ApplySkin(skin);

            Canvas.ForceUpdateCanvases();
            LayoutRebuilder.ForceRebuildLayoutImmediate(demo.InventoryContent);
            Canvas.ForceUpdateCanvases();

            var sceneDir = "Assets/AETHERQOR_UI_POC/Scenes";
            if (!AssetDatabase.IsValidFolder(sceneDir))
            {
                if (!AssetDatabase.IsValidFolder("Assets/AETHERQOR_UI_POC"))
                    AssetDatabase.CreateFolder("Assets", "AETHERQOR_UI_POC");
                AssetDatabase.CreateFolder("Assets/AETHERQOR_UI_POC", "Scenes");
            }
            string scenePath = sceneDir + "/AQ_InventoryScrollDemo_DarkFantasy.unity";
            EditorSceneManager.SaveScene(scene, scenePath);

            var cam = GameObject.Find("AQ_UI_Camera")?.GetComponent<Camera>();
            if (cam == null) throw new Exception("AQ_UI_Camera not found");

            int emptySlots = root.GetComponentsInChildren<Transform>(true).Count(t => t.name.StartsWith("EmptySlot_"));
            if (emptySlots != 48) throw new Exception("Expected 48 empty inventory slots, got " + emptySlots);
            if (demo.Model3DAnchor == null) throw new Exception("3D model anchor missing");
            if (demo.InventoryScroll == null || demo.InventoryScroll.horizontal || !demo.InventoryScroll.vertical)
                throw new Exception("Inventory ScrollRect is not vertical-only");

            demo.SetScroll01(0f);
            float topY = demo.InventoryContent.anchoredPosition.y;
            Capture(cam, Path.Combine(outDir, "AQ_DARK_TOP.png"));

            demo.SetScroll01(0.5f);
            float midY = demo.InventoryContent.anchoredPosition.y;
            Capture(cam, Path.Combine(outDir, "AQ_DARK_MIDDLE.png"));

            demo.SetScroll01(1f);
            float bottomY = demo.InventoryContent.anchoredPosition.y;
            Capture(cam, Path.Combine(outDir, "AQ_DARK_BOTTOM.png"));

            float travel = Mathf.Abs(bottomY - topY);
            if (travel < 700f)
                throw new Exception($"Scroll content travel too small: {travel:F2}px");

            const int count = 37;
            for (int i = 0; i < count; i++)
            {
                float t = i / (float)(count - 1);
                demo.SetScroll01(Mathf.SmoothStep(0f, 1f, t));
                Capture(cam, Path.Combine(frames, $"frame_{i:000}.png"));
            }

            File.WriteAllText(Path.Combine(outDir, "validation.txt"),
                "AETHERQOR DARK FANTASY UNITY POC\n" +
                "BaseDesign=approved generated screen used 1:1 as Unity texture\n" +
                $"SkinResolution={skin.width}x{skin.height}\n" +
                $"UnityReferenceResolution={W}x{H}\n" +
                "ModelArea=EMPTY dedicated AETHERQOR_MODEL_3D_ANCHOR\n" +
                $"EmptyInventorySlots={emptySlots}\n" +
                "InventoryColumns=4\n" +
                "ItemIcons=0\n" +
                "TileIcons=0\n" +
                "VerticalScroll=true\n" +
                "HorizontalScroll=false\n" +
                "Inertia=true\n" +
                $"ContentTravelPx={travel:F2}\n" +
                $"TopY={topY:F2}\nMiddleY={midY:F2}\nBottomY={bottomY:F2}\n" +
                $"Scene={scenePath}\n");

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("[AQ-DARK-UI] PASS output=" + outDir);
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
