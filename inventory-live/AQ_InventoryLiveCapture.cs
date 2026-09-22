#if UNITY_EDITOR
using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.UI;

[InitializeOnLoad]
public static class AQ_InventoryLiveCapture
{
    const string RUN = "AQ_INV_LIVE_CAPTURE_RUN";
    const string SCENE = "Assets/Aetherqor/Scenes/AQ0062_BDMStyle_CombatSlice_Candidate.unity";
    const string BG = "Assets/Aetherqor/Resources/AQ/V3/Ekrany/E12_Ekwipunek_Tlo_4K.png";
    static int frames;
    static bool built;

    static AQ_InventoryLiveCapture()
    {
        if (EditorPrefs.GetBool(RUN, false)) EditorApplication.update += Tick;
    }

    public static void StartCapture()
    {
        string data = Application.dataPath.Replace('\','/');
        if (!data.EndsWith("/Aetherqor/Gra/Assets", StringComparison.OrdinalIgnoreCase))
            throw new Exception("WRONG PROJECT: " + data);

        ConfigureTexture();
        string sceneFs = Path.Combine(Path.GetDirectoryName(Application.dataPath), SCENE.Replace("/", Path.DirectorySeparatorChar.ToString()));\n        if (!File.Exists(sceneFs)) throw new Exception("Scene missing: " + sceneFs);
        EditorSceneManager.OpenScene(SCENE, OpenSceneMode.Single);
        EditorPrefs.SetBool(RUN, true);
        frames = 0; built = false;
        EditorApplication.update -= Tick;
        EditorApplication.update += Tick;
        EditorApplication.isPlaying = true;
    }

    static void ConfigureTexture()
    {
        AssetDatabase.ImportAsset(BG, ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
        var ti = AssetImporter.GetAtPath(BG) as TextureImporter;
        if (ti == null) throw new Exception("TextureImporter missing: " + BG);
        ti.textureType = TextureImporterType.Default;
        ti.sRGBTexture = true;
        ti.alphaIsTransparency = false;
        ti.mipmapEnabled = false;
        ti.textureCompression = TextureImporterCompression.Uncompressed;
        ti.crunchedCompression = false;
        ti.maxTextureSize = 8192;
        ti.npotScale = TextureImporterNPOTScale.None;
        ti.SaveAndReimport();
    }

    static void Tick()
    {
        if (!EditorPrefs.GetBool(RUN, false)) { EditorApplication.update -= Tick; return; }
        if (!EditorApplication.isPlaying) return;
        frames++;

        try
        {
            if (!built && frames > 60)
            {
                AQ_VberAIEkranEkwipunek.Wlacz();
                built = true;
            }

            if (!built) return;
            Texture portrait = AQ_VberAIPortretGracza.Tekstura();
            if (portrait == null)
            {
                if (frames < 480) return;
                throw new Exception("Portrait RT is null after wait. Stan=" + AQ_VberAIPortretGracza.Stan);
            }

            if (frames < 100) return;

            Canvas.ForceUpdateCanvases();
            var sr = AQ_VberAIEkranEkwipunek.Scroll;
            if (sr == null) throw new Exception("ScrollRect missing");
            if (!sr.vertical || sr.horizontal) throw new Exception("Wrong ScrollRect axes");
            if (sr.content == null || sr.viewport == null || sr.content.rect.height <= sr.viewport.rect.height)
                throw new Exception($"Content not scrollable content={sr.content?.rect.height} viewport={sr.viewport?.rect.height}");

            string outDir = Environment.GetEnvironmentVariable("AQ_CAPTURE_OUT");
            if (string.IsNullOrEmpty(outDir)) outDir = Path.Combine(Path.GetDirectoryName(Application.dataPath), "AQ_InventoryCapture");
            Directory.CreateDirectory(outDir);

            sr.verticalNormalizedPosition = 1f;
            Canvas.ForceUpdateCanvases();
            RenderUI(Path.Combine(outDir,"Inventory_TOP.png"),2340,1080);
            RenderUI(Path.Combine(outDir,"Inventory_4K.png"),4680,2160);

            sr.verticalNormalizedPosition = 0.28f;
            Canvas.ForceUpdateCanvases();
            RenderUI(Path.Combine(outDir,"Inventory_SCROLLED.png"),2340,1080);

            var safe = AQ_VberAIEkranEkwipunek.SafeArea;
            if (safe == null) throw new Exception("SafeArea fitter missing");
            safe.ApplyForTest(new Rect(132f,0f,2292f,1179f),2556,1179);
            Canvas.ForceUpdateCanvases();
            RenderUI(Path.Combine(outDir,"Inventory_PHONE_SAFEAREA.png"),2556,1179);
            safe.Apply();

            int icons = 0;
            var root = GameObject.Find(AQ_VberAIEkranEkwipunek.NAZWA_ROOT);
            foreach (var im in root.GetComponentsInChildren<Image>(true))
                if (im.name == "Ikona" && im.enabled && im.sprite != null) icons++;

            string result = AQ_VberAIEkranEkwipunek.Walidacja();
            File.WriteAllText(Path.Combine(outDir,"validation.txt"),
                "AETHERQOR INVENTORY LIVE UNITY PLAY MODE\n"+
                "Project="+Application.dataPath+"\n"+
                "Scene="+SCENE+"\n"+
                "Figma=https://www.figma.com/design/FTxHbKquUz80UmikO4hVPv node=1:2\n"+
                "ScreenValidation="+result+"\n"+
                "Portrait="+AQ_VberAIPortretGracza.Stan+"\n"+
                "PortraitRT="+portrait.width+"x"+portrait.height+"\n"+
                "ScrollVertical="+sr.vertical+"\nScrollHorizontal="+sr.horizontal+"\n"+
                "ContentHeight="+sr.content.rect.height+"\nViewportHeight="+sr.viewport.rect.height+"\n"+
                "ScrolledAnchoredY="+sr.content.anchoredPosition.y+"\n"+
                "EnabledItemIcons="+icons+"\n"+
                "SafeAreaHelper=PASS\n"+
                "Capture2340x1080=PASS\nCapture4680x2160=PASS\n");

            if (icons != 0) throw new Exception("Non-empty item icons detected: " + icons);
            if (result != "PASS") throw new Exception(result);

            Finish(0);
        }
        catch(Exception ex)
        {
            Debug.LogException(ex);
            string outDir = Environment.GetEnvironmentVariable("AQ_CAPTURE_OUT");
            if (!string.IsNullOrEmpty(outDir)) { Directory.CreateDirectory(outDir); File.WriteAllText(Path.Combine(outDir,"FAIL.txt"),ex.ToString()); }
            Finish(2);
        }
    }

    static void RenderUI(string path, int width, int height)
    {
        var root = GameObject.Find(AQ_VberAIEkranEkwipunek.NAZWA_ROOT);
        if (root == null) throw new Exception("Inventory root missing during capture");
        var canvas = root.GetComponent<Canvas>();
        if (canvas == null) throw new Exception("Inventory canvas missing");

        var portraitCam = GameObject.Find("AQ_VberAI_KameraPodgladu")?.GetComponent<Camera>();
        if (portraitCam != null) portraitCam.Render();

        var camGo = new GameObject("AQ_CAPTURE_CAMERA");
        var cam = camGo.AddComponent<Camera>();
        cam.clearFlags = CameraClearFlags.SolidColor;
        cam.backgroundColor = Color.black;
        cam.cullingMask = ~0;
        cam.orthographic = true;
        cam.transform.position = new Vector3(0,0,-10);

        var rt = new RenderTexture(width,height,24,RenderTextureFormat.ARGB32);
        var prevMode = canvas.renderMode;
        var prevCam = canvas.worldCamera;
        float prevPlane = canvas.planeDistance;
        canvas.renderMode = RenderMode.ScreenSpaceCamera;
        canvas.worldCamera = cam;
        canvas.planeDistance = 1f;
        cam.targetTexture = rt;
        Canvas.ForceUpdateCanvases();
        cam.Render();

        var prev = RenderTexture.active;
        RenderTexture.active = rt;
        var tex = new Texture2D(width,height,TextureFormat.RGBA32,false);
        tex.ReadPixels(new Rect(0,0,width,height),0,0,false);
        tex.Apply(false,false);
        File.WriteAllBytes(path,tex.EncodeToPNG());

        RenderTexture.active = prev;
        cam.targetTexture = null;
        canvas.renderMode = prevMode;
        canvas.worldCamera = prevCam;
        canvas.planeDistance = prevPlane;
        UnityEngine.Object.Destroy(tex);
        rt.Release(); UnityEngine.Object.Destroy(rt); UnityEngine.Object.Destroy(camGo);
    }

    static void Finish(int code)
    {
        EditorPrefs.SetBool(RUN,false);
        EditorApplication.update -= Tick;
        EditorApplication.Exit(code);
    }
}
#endif
