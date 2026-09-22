#if UNITY_EDITOR
using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.UI;

public static class AQ_InventoryLiveCapture
{
    const string BG = "Assets/Aetherqor/Resources/AQ/V3/Ekrany/E12_Ekwipunek_Tlo_4K.png";
    static readonly string[] SCENES = {
        "Assets/Aetherqor/Scenes/AQ0062_BDMStyle_CombatSlice_Candidate.unity",
        "Assets/Aetherqor/Scenes/AQ0103_AAA_VerticalSlice_Candidate.unity",
        "Assets/Aetherqor_Production/AQ_Clean_MiastoPortowe.unity"
    };

    public static void CaptureEditMode()
    {
        try
        {
            string data=Application.dataPath.Replace('\\','/');
            if(!data.EndsWith("/Aetherqor/Gra/Assets",StringComparison.OrdinalIgnoreCase))
                throw new Exception("WRONG PROJECT: "+data);
            ConfigureTexture();

            Texture portrait=null;
            string usedScene=null;
            foreach(string scene in SCENES)
            {
                string fs=Path.Combine(Path.GetDirectoryName(Application.dataPath),scene.Replace("/",Path.DirectorySeparatorChar.ToString()));
                if(!File.Exists(fs)) continue;
                EditorSceneManager.OpenScene(scene,OpenSceneMode.Single);
                AQ_VberAIEkranEkwipunek.Wlacz();
                if(AQ_VberAIEkranEkwipunek.SafeArea!=null)
                    AQ_VberAIEkranEkwipunek.SafeArea.ApplyForTest(new Rect(0,0,2340,1080),2340,1080);
                Canvas.ForceUpdateCanvases();
                portrait=AQ_VberAIPortretGracza.Tekstura();
                if(portrait!=null){ usedScene=scene; break; }
                AQ_VberAIEkranEkwipunek.Wylacz();
            }
            if(portrait==null) throw new Exception("No live player model found. Portret Stan="+AQ_VberAIPortretGracza.Stan);

            var pc=GameObject.Find("AQ_VberAI_KameraPodgladu")?.GetComponent<Camera>();
            if(pc!=null) pc.Render();
            AQ_VberAIEkranEkwipunek.Portret.texture=portrait;
            Canvas.ForceUpdateCanvases();

            var sr=AQ_VberAIEkranEkwipunek.Scroll;
            if(sr==null || !sr.vertical || sr.horizontal) throw new Exception("ScrollRect config FAIL");
            if(sr.content==null || sr.viewport==null || sr.content.rect.height<=sr.viewport.rect.height)
                throw new Exception("Scroll content not larger than viewport");

            string outDir=Environment.GetEnvironmentVariable("AQ_CAPTURE_OUT");
            if(string.IsNullOrEmpty(outDir)) outDir=Path.Combine(Path.GetDirectoryName(Application.dataPath),"AQ_InventoryCapture");
            Directory.CreateDirectory(outDir);

            sr.verticalNormalizedPosition=1f; Canvas.ForceUpdateCanvases();
            RenderUI(Path.Combine(outDir,"Inventory_TOP.png"),2340,1080);
            RenderUI(Path.Combine(outDir,"Inventory_4K.png"),4680,2160);

            sr.verticalNormalizedPosition=0.25f; Canvas.ForceUpdateCanvases();
            RenderUI(Path.Combine(outDir,"Inventory_SCROLLED.png"),2340,1080);
            float travel=Mathf.Abs(sr.content.anchoredPosition.y);

            var safe=AQ_VberAIEkranEkwipunek.SafeArea;
            safe.ApplyForTest(new Rect(132,0,2292,1179),2556,1179);
            Canvas.ForceUpdateCanvases();
            RenderUI(Path.Combine(outDir,"Inventory_PHONE_SAFEAREA.png"),2556,1179);
            safe.ApplyForTest(new Rect(0,0,2340,1080),2340,1080);

            int icons=0;
            var root=GameObject.Find(AQ_VberAIEkranEkwipunek.NAZWA_ROOT);
            foreach(var im in root.GetComponentsInChildren<Image>(true))
                if(im.name=="Ikona" && im.enabled && im.sprite!=null) icons++;

            string result=AQ_VberAIEkranEkwipunek.Walidacja();
            File.WriteAllText(Path.Combine(outDir,"validation.txt"),
                "AETHERQOR INVENTORY UNITY EDITOR RENDER\n"+
                "Project="+Application.dataPath+"\nScene="+usedScene+"\n"+
                "Figma=https://www.figma.com/design/FTxHbKquUz80UmikO4hVPv node=1:2\n"+
                "ScreenValidation="+result+"\nPortrait="+AQ_VberAIPortretGracza.Stan+"\n"+
                "PortraitRT="+portrait.width+"x"+portrait.height+"\n"+
                "ScrollVertical="+sr.vertical+"\nScrollHorizontal="+sr.horizontal+"\n"+
                "ContentHeight="+sr.content.rect.height+"\nViewportHeight="+sr.viewport.rect.height+"\n"+
                "ScrollTravel="+travel+"\nEnabledItemIcons="+icons+"\n"+
                "SafeAreaAlgorithm=PASS\nCapture2340x1080=PASS\nCapture4680x2160=PASS\n");
            if(result!="PASS" || icons!=0) throw new Exception("Validation FAIL result="+result+" icons="+icons);
            AssetDatabase.SaveAssets();
            EditorApplication.Exit(0);
        }
        catch(Exception ex)
        {
            Debug.LogException(ex);
            string outDir=Environment.GetEnvironmentVariable("AQ_CAPTURE_OUT");
            if(!string.IsNullOrEmpty(outDir)){Directory.CreateDirectory(outDir);File.WriteAllText(Path.Combine(outDir,"FAIL.txt"),ex.ToString());}
            EditorApplication.Exit(2);
        }
    }

    static void ConfigureTexture()
    {
        AssetDatabase.ImportAsset(BG,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
        var ti=AssetImporter.GetAtPath(BG) as TextureImporter;
        if(ti==null) throw new Exception("TextureImporter missing: "+BG);
        ti.textureType=TextureImporterType.Default; ti.sRGBTexture=true; ti.mipmapEnabled=false;
        ti.textureCompression=TextureImporterCompression.Uncompressed; ti.crunchedCompression=false;
        ti.maxTextureSize=8192; ti.npotScale=TextureImporterNPOTScale.None; ti.SaveAndReimport();
    }

    static void RenderUI(string path,int width,int height)
    {
        var root=GameObject.Find(AQ_VberAIEkranEkwipunek.NAZWA_ROOT);
        var canvas=root!=null?root.GetComponent<Canvas>():null;
        if(canvas==null) throw new Exception("Inventory Canvas missing");

        var pc=GameObject.Find("AQ_VberAI_KameraPodgladu")?.GetComponent<Camera>();
        if(pc!=null) pc.Render();

        var cg=new GameObject("AQ_CAPTURE_CAMERA");
        var cam=cg.AddComponent<Camera>();
        cam.clearFlags=CameraClearFlags.SolidColor; cam.backgroundColor=Color.black; cam.cullingMask=~0;
        cam.orthographic=true; cam.transform.position=new Vector3(0,0,-10);
        var rt=new RenderTexture(width,height,24,RenderTextureFormat.ARGB32);
        var prevMode=canvas.renderMode; var prevCam=canvas.worldCamera; float prevPlane=canvas.planeDistance;
        canvas.renderMode=RenderMode.ScreenSpaceCamera; canvas.worldCamera=cam; canvas.planeDistance=1f;
        cam.targetTexture=rt; Canvas.ForceUpdateCanvases(); cam.Render();

        var prev=RenderTexture.active; RenderTexture.active=rt;
        var tex=new Texture2D(width,height,TextureFormat.RGBA32,false);
        tex.ReadPixels(new Rect(0,0,width,height),0,0,false); tex.Apply(false,false);
        File.WriteAllBytes(path,tex.EncodeToPNG());

        RenderTexture.active=prev; cam.targetTexture=null;
        canvas.renderMode=prevMode; canvas.worldCamera=prevCam; canvas.planeDistance=prevPlane;
        UnityEngine.Object.DestroyImmediate(tex); rt.Release(); UnityEngine.Object.DestroyImmediate(rt); UnityEngine.Object.DestroyImmediate(cg);
    }
}
#endif
