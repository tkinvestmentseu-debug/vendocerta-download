using UnityEngine;
using UnityEngine.UI;
using BDM = AQ_VberAIStylBDM;
using Kit = AQ_VberAIKit;

public static class AQ_VberAIEkranEkwipunek
{
    public const string NAZWA_ROOT = "AQ_VberAI_WarstwaEkwipunek";
    private const float W = 1846f, H = 852f;
    private const int SORTING = 1010;
    private const string TLO = "AQ/V3/Ekrany/E12_Ekwipunek_Tlo_4K";

    private static GameObject _root;
    private static RectTransform _design;
    private static RawImage _portret;
    private static ScrollRect _scroll;
    private static RectTransform _content;
    private static AQ_VberAISafeAreaFitter _safe;
    private static bool _widoczny;

    public static ScrollRect Scroll => _scroll;
    public static RawImage Portret => _portret;
    public static RectTransform DesignRoot => _design;
    public static AQ_VberAISafeAreaFitter SafeArea => _safe;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    private static void Start_()
    {
        UnityEngine.SceneManagement.SceneManager.sceneLoaded -= PoZaladowaniu;
        UnityEngine.SceneManagement.SceneManager.sceneLoaded += PoZaladowaniu;
    }

    private static void PoZaladowaniu(UnityEngine.SceneManagement.Scene s, UnityEngine.SceneManagement.LoadSceneMode m)
    {
        bool byl = _widoczny;
        _root = null; _design = null; _portret = null; _scroll = null; _content = null; _safe = null;
        if (byl) Wlacz();
    }

    public static void Wlacz()
    {
        if (_root == null) Zbuduj();
        if (_root == null) return;
        _root.SetActive(true);
        _widoczny = true;
        OdswiezPortret();
    }

    public static void Wylacz()
    {
        _widoczny = false;
        AQ_VberAIPortretGracza.Pokaz(false);
        if (_root != null) _root.SetActive(false);
    }

    private static void Zbuduj()
    {
        var stary = GameObject.Find(NAZWA_ROOT);
        if (stary != null) Object.Destroy(stary);

        _root = new GameObject(NAZWA_ROOT);
        var canvas = _root.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvas.sortingOrder = SORTING;
        _root.AddComponent<GraphicRaycaster>();

        var scaler = _root.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(W, H);
        scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
        scaler.matchWidthOrHeight = 0.5f;

        _design = AQ_VberAIUklad.Prostokat(_root.transform, "AQ_DesignRoot", new Rect(0,0,W,H));
        _design.anchorMin = _design.anchorMax = new Vector2(0.5f,0.5f);
        _design.pivot = new Vector2(0.5f,0.5f);
        _design.sizeDelta = new Vector2(W,H);
        _design.anchoredPosition = Vector2.zero;
        _safe = _design.gameObject.AddComponent<AQ_VberAISafeAreaFitter>();
        _safe.referenceSize = new Vector2(W,H);

        BudujTlo(_design);
        BudujTop(_design);
        BudujLewyNav(_design);
        BudujGear(_design);
        BudujRuny(_design);
        BudujPortret(_design);
        BudujInventory(_design);
        BudujDol(_design);
        _safe.Apply();
    }

    private static void BudujTlo(Transform parent)
    {
        var rt = AQ_VberAIUklad.Prostokat(parent, "AQ_Tlo", new Rect(0,0,W,H));
        var ri = rt.gameObject.AddComponent<RawImage>();
        ri.texture = Resources.Load<Texture2D>(TLO);
        ri.color = Color.white;
        ri.raycastTarget = false;
        if (ri.texture == null)
        {
            var im = rt.gameObject.AddComponent<Image>();
            im.color = BDM.Hex("050609");
            im.raycastTarget = false;
        }
    }

    private static RectTransform Panel(Transform p, string name, Rect r, BDM.Powierzchnia s = BDM.Powierzchnia.Panel)
        => BDM.Panel(p, name, r, s, false, 8);

    private static void BudujTop(Transform p)
    {
        var top = Panel(p, "AQ_TopBar", new Rect(0,0,1846,93), BDM.Powierzchnia.Modal);
        Kolo(top, "AQ_TopPortrait", new Rect(18,5,82,82), BDM.ZLOTO_JASNE, 3f);
        Panel(top, "AQ_TopLineA", new Rect(116,18,258,16), BDM.Powierzchnia.Inspektor);
        Panel(top, "AQ_TopLineB", new Rect(116,49,258,16), BDM.Powierzchnia.Inspektor);
        float[] px = { 892f, 1110f, 1328f };
        for (int i=0;i<px.Length;i++)
            Kit.KapsulaWaluty(top, new Rect(px[i],13,202,54), null, "", null).name = "AQ_ResourcePill_"+i;
        for (int i=0;i<5;i++)
            Kolo(top, "AQ_TopCircle_"+i, new Rect(1546+i*57,16,50,50), BDM.ZLOTO, 2f);
    }

    private static void BudujLewyNav(Transform p)
    {
        var nav = Panel(p, "AQ_LeftNav", new Rect(11,121.5f,110.4f,560.1f), BDM.Powierzchnia.Modal);
        for (int i=0;i<6;i++)
        {
            var s = Kit.Slot(nav, "AQ_LeftNavSlot_"+i, new Rect(11,13+i*87,88,80), BDM.Rzadkosc.Legendary);
            Kit.SlotUstaw(s, null, null);
        }
    }

    private static void BudujGear(Transform p)
    {
        var left = AQ_VberAIUklad.Prostokat(p, "AQ_GearSlotyLewe", new Rect(0,0,W,H));
        var right = AQ_VberAIUklad.Prostokat(p, "AQ_GearSlotyPrawe", new Rect(0,0,W,H));
        const float size=121.5f, xL=306.1f, xR=954.6f, y0=112.0f, step=127.8f;
        for(int i=0;i<5;i++)
        {
            var a=Kit.Slot(left,"GearL_"+i,new Rect(xL,y0+i*step,size,size),BDM.Rzadkosc.Legendary); Kit.SlotUstaw(a,null,null);
            var b=Kit.Slot(right,"GearR_"+i,new Rect(xR,y0+i*step,size,size),BDM.Rzadkosc.Legendary); Kit.SlotUstaw(b,null,null);
        }
    }

    private static void BudujRuny(Transform p)
    {
        var gold = AQ_VberAIUklad.Prostokat(p,"AQ_RunyZlote",new Rect(0,0,W,H));
        var purple = AQ_VberAIUklad.Prostokat(p,"AQ_RunyFioletowe",new Rect(0,0,W,H));
        const float size=113.6f, y0=161.7f, step=123.9f;
        for(int i=0;i<4;i++)
        {
            Kolo(gold,"RunaGold_"+i,new Rect(173.6f,y0+i*step,size,size),BDM.ZLOTO_JASNE,5f);
            Kolo(purple,"RunaPurple_"+i,new Rect(1092.7f,y0+i*step,size,size),BDM.R_EPIC,5f);
        }
    }

    private static void BudujPortret(Transform p)
    {
        var host = AQ_VberAIUklad.Prostokat(p,"AQ_PodgladPostaci",new Rect(449.7f,118.3f,504.9f,639f));
        var child = new GameObject("RawImage", typeof(RectTransform), typeof(RawImage), typeof(AspectRatioFitter));
        child.transform.SetParent(host, false);
        var crt = child.GetComponent<RectTransform>();
        crt.anchorMin = Vector2.zero; crt.anchorMax = Vector2.one; crt.offsetMin = Vector2.zero; crt.offsetMax = Vector2.zero;
        _portret = child.GetComponent<RawImage>();
        _portret.color = Color.white;
        _portret.raycastTarget = true;
        var ar = child.GetComponent<AspectRatioFitter>();
        ar.aspectMode = AspectRatioFitter.AspectMode.FitInParent;
        ar.aspectRatio = 768f/1024f;
        AQ_VberAIPortretGracza.PodepnijObrot(_portret);
    }

    private static void OdswiezPortret()
    {
        if (_portret == null) return;
        AQ_VberAIPortretGracza.Pokaz(true);
        _portret.texture = AQ_VberAIPortretGracza.Tekstura();
    }

    private static void BudujInventory(Transform p)
    {
        Panel(p,"AQ_PanelEkwipunku",new Rect(1250.4f,98.6f,544.3f,615.2f),BDM.Powierzchnia.Modal);
        var header = Panel(p,"AQ_NaglowekPanelu",new Rect(1265.4f,115.2f,497f,78.9f),BDM.Powierzchnia.Inspektor);
        float tabW=67f, gap=12.5f;
        for(int i=0;i<6;i++)
            Panel(header,"AQ_HeaderTab_"+i,new Rect(10+i*(tabW+gap),9,tabW,60),i==0?BDM.Powierzchnia.Wybrany:BDM.Powierzchnia.Tabs);

        _scroll = Kit.PrzewijanieRamka(p,new Rect(1260.4f,197.0f,520.5f,503.5f),out _content,false);
        _scroll.name = "AQ_InventoryScrollRect";
        _content.name = "AQ_InventoryContent";

        const float slot=107.3f, gapS=9f;
        int rows=10, cols=4;
        _content.sizeDelta = new Vector2(0f, rows*slot + (rows-1)*gapS + 16f);
        for(int r=0;r<rows;r++)
            for(int c=0;c<cols;c++)
            {
                int idx=r*cols+c;
                var s=Kit.Slot(_content,"Plecak_"+idx,new Rect(8+c*(slot+gapS),8+r*(slot+gapS),slot,slot),BDM.Rzadkosc.Legendary);
                Kit.SlotUstaw(s,null,null);
            }
        _scroll.verticalNormalizedPosition = 1f;
    }

    private static void BudujDol(Transform p)
    {
        var bottom=Panel(p,"AQ_BottomBar",new Rect(0,733.6f,1846,118.4f),BDM.Powierzchnia.Modal);
        const float big=94.7f, small=74.2f;
        for(int i=0;i<5;i++) Kolo(bottom,"AQ_BottomLeft_"+i,new Rect(20.5f+i*101f,10,big,big),BDM.ZLOTO,3f);
        for(int i=0;i<5;i++) Kolo(bottom,"AQ_BottomMid_"+i,new Rect(732f+i*85.2f,22,small,small),BDM.ZLOTO,2f);
        for(int i=0;i<2;i++) Kolo(bottom,"AQ_BottomRight_"+i,new Rect(1615f+i*104f,10,big,big),BDM.ZLOTO,3f);
    }

    private static RectTransform Kolo(Transform p,string name,Rect r,Color ring,float ringWidth)
    {
        var rt=AQ_VberAIUklad.Prostokat(p,name,r);
        var outer=rt.gameObject.AddComponent<Image>();
        outer.sprite=BDM.Kolo(); outer.color=ring; outer.raycastTarget=false;
        float m=Mathf.Max(2f,ringWidth);
        var inner=AQ_VberAIUklad.Prostokat(rt,"Wnetrze",new Rect(m,m,r.width-2*m,r.height-2*m));
        var ii=inner.gameObject.AddComponent<Image>(); ii.sprite=BDM.Kolo(); ii.color=BDM.P_INSPEKTOR; ii.raycastTarget=false;
        return rt;
    }

    public static string Walidacja()
    {
        if (_root==null) return "FAIL root=null";
        if (_scroll==null || !_scroll.vertical || _scroll.horizontal) return "FAIL scroll-config";
        if (_content==null || _scroll.viewport==null || _content.rect.height<=_scroll.viewport.rect.height) return "FAIL content<=viewport";
        if (_portret==null) return "FAIL portrait=null";
        return "PASS";
    }
}
