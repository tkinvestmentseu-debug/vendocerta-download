using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

public class AetherqorInventoryScrollDemo : MonoBehaviour
{
    public ScrollRect InventoryScroll { get; private set; }
    public RectTransform InventoryContent { get; private set; }

    static readonly Color Bg = new Color(0.015f, 0.018f, 0.022f, 1f);
    static readonly Color Panel = new Color(0.025f, 0.028f, 0.032f, 0.96f);
    static readonly Color Panel2 = new Color(0.045f, 0.047f, 0.052f, 0.98f);
    static readonly Color Gold = new Color(0.53f, 0.39f, 0.20f, 1f);
    static readonly Color GoldBright = new Color(0.83f, 0.62f, 0.28f, 1f);
    static readonly Color Violet = new Color(0.45f, 0.16f, 0.70f, 1f);
    static readonly Color Red = new Color(0.42f, 0.055f, 0.045f, 1f);

    public void BuildNow()
    {
        if (transform.Find("AQ_UI_ROOT") != null) return;

        EnsureEventSystem();

        var camGo = new GameObject("AQ_UI_Camera", typeof(Camera));
        camGo.transform.SetParent(transform, false);
        var cam = camGo.GetComponent<Camera>();
        cam.clearFlags = CameraClearFlags.SolidColor;
        cam.backgroundColor = Bg;
        cam.orthographic = true;
        cam.orthographicSize = 5f;
        cam.transform.position = new Vector3(0, 0, -10);

        var canvasGo = new GameObject("AQ_UI_ROOT", typeof(RectTransform), typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
        canvasGo.transform.SetParent(transform, false);
        var canvas = canvasGo.GetComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceCamera;
        canvas.worldCamera = cam;
        canvas.planeDistance = 1f;

        var scaler = canvasGo.GetComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(2340, 1080);
        scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
        scaler.matchWidthOrHeight = 0.5f;

        var root = canvasGo.GetComponent<RectTransform>();
        Stretch(root, 0, 0, 1, 1, 0, 0, 0, 0);

        // Overall atmosphere
        AddPanel(root, "Backdrop", new Vector2(0,0), new Vector2(1,1), new Vector2(0,0), new Vector2(0,0), new Color(0.01f,0.012f,0.015f,1));
        AddPanel(root, "TopBand", new Vector2(0,1), new Vector2(1,1), new Vector2(0,-92), new Vector2(0,0), new Color(0.012f,0.014f,0.018f,0.98f));
        AddLine(root, "TopGoldLine", new Vector2(0,1), new Vector2(1,1), new Vector2(0,-94), new Vector2(0,-90), Gold);

        // Left vertical navigation
        var leftNav = AddPanel(root, "LeftNav", new Vector2(0,0.09f), new Vector2(0,0.91f), new Vector2(18,0), new Vector2(116,0), Panel);
        for (int i=0;i<6;i++) AddIconButton(leftNav, "Nav_"+i, i==0 ? GoldBright : Gold, 74, new Vector2(49, -55 - i*118));

        // Center presentation zone
        var center = AddPanel(root, "CharacterZone", new Vector2(0,0), new Vector2(0,1), new Vector2(130,38), new Vector2(1135,-112), new Color(0.012f,0.014f,0.018f,1));
        AddPanel(center, "ModelVoid", new Vector2(0,0), new Vector2(1,1), new Vector2(230,80), new Vector2(-230,-70), new Color(0.018f,0.021f,0.025f,1));
        AddRing(center, "ModelPedestalOuter", new Vector2(0.5f,0), new Vector2(0.5f,0), new Vector2(0,148), 430, 92, Gold);
        AddRing(center, "ModelPedestalInner", new Vector2(0.5f,0), new Vector2(0.5f,0), new Vector2(0,148), 348, 56, new Color(0.16f,0.12f,0.08f,1));

        // 8 runes: 4 Elion + 4 Hadum, mobile-sized.
        for (int i=0;i<4;i++)
        {
            AddRuneSlot(center, "ElionRune_"+i, new Vector2(165, 710 - i*158), 126, GoldBright, new Color(0.20f,0.13f,0.04f,1));
            AddRuneSlot(center, "HadumRune_"+i, new Vector2(840, 710 - i*158), 126, new Color(0.68f,0.35f,1f,1), new Color(0.12f,0.025f,0.20f,1));
        }

        // Gear slots around the model anchor, large enough for mobile.
        float[] y = { 760, 598, 436, 274, 112 };
        for (int i=0;i<5;i++)
        {
            AddGearSlot(center, "GearL_"+i, new Vector2(315, y[i]), 128, i);
            AddGearSlot(center, "GearR_"+i, new Vector2(690, y[i]), 128, i+5);
        }

        // Right inventory, fixed frame + fixed tabs + true vertical scroll viewport
        var right = AddPanel(root, "InventoryFrame", new Vector2(1,0), new Vector2(1,1), new Vector2(-1135,38), new Vector2(-26,-112), Panel);
        AddBorder(right, Gold, 4f);

        var tabs = AddPanel(right, "FixedTabs", new Vector2(0,1), new Vector2(1,1), new Vector2(20,-132), new Vector2(-52,-24), Panel2);
        for (int i=0;i<6;i++)
        {
            var b = AddPanel(tabs, "Tab_"+i, new Vector2(0,0), new Vector2(0,0), new Vector2(12+i*142,12), new Vector2(128+i*142,96), i==0 ? new Color(0.23f,0.16f,0.075f,1) : new Color(0.035f,0.038f,0.043f,1));
            AddBorder(b, i==0 ? GoldBright : new Color(0.22f,0.18f,0.12f,1), i==0 ? 3f : 1.5f);
            AddGlyph(b, i, i==0 ? GoldBright : new Color(0.52f,0.50f,0.46f,1));
        }

        var viewport = AddPanel(right, "InventoryViewport", new Vector2(0,0), new Vector2(1,1), new Vector2(24,30), new Vector2(-66,-158), new Color(0.012f,0.014f,0.017f,1));
        var mask = viewport.gameObject.AddComponent<RectMask2D>();

        var contentGo = new GameObject("InventoryContent", typeof(RectTransform), typeof(GridLayoutGroup), typeof(ContentSizeFitter));
        contentGo.transform.SetParent(viewport, false);
        var content = contentGo.GetComponent<RectTransform>();
        content.anchorMin = new Vector2(0,1);
        content.anchorMax = new Vector2(1,1);
        content.pivot = new Vector2(0.5f,1);
        content.anchoredPosition = Vector2.zero;
        content.sizeDelta = new Vector2(0,0);
        InventoryContent = content;

        var grid = contentGo.GetComponent<GridLayoutGroup>();
        grid.padding = new RectOffset(8,8,8,8);
        grid.cellSize = new Vector2(148,148);
        grid.spacing = new Vector2(18,18);
        grid.startCorner = GridLayoutGroup.Corner.UpperLeft;
        grid.startAxis = GridLayoutGroup.Axis.Horizontal;
        grid.childAlignment = TextAnchor.UpperLeft;
        grid.constraint = GridLayoutGroup.Constraint.FixedColumnCount;
        grid.constraintCount = 4;

        var fitter = contentGo.GetComponent<ContentSizeFitter>();
        fitter.verticalFit = ContentSizeFitter.FitMode.PreferredSize;
        fitter.horizontalFit = ContentSizeFitter.FitMode.Unconstrained;

        for (int i=0;i<48;i++) AddInventorySlot(content, i);

        var scroll = right.gameObject.AddComponent<ScrollRect>();
        scroll.viewport = viewport;
        scroll.content = content;
        scroll.horizontal = false;
        scroll.vertical = true;
        scroll.movementType = ScrollRect.MovementType.Elastic;
        scroll.elasticity = 0.085f;
        scroll.inertia = true;
        scroll.decelerationRate = 0.125f;
        scroll.scrollSensitivity = 58f;
        scroll.verticalNormalizedPosition = 1f;
        InventoryScroll = scroll;

        // Large mobile scrollbar
        var barBg = AddPanel(right, "ScrollbarBG", new Vector2(1,0), new Vector2(1,1), new Vector2(-44,34), new Vector2(-16,-160), new Color(0.055f,0.048f,0.037f,1));
        var slider = barBg.gameObject.AddComponent<Scrollbar>();
        slider.direction = Scrollbar.Direction.BottomToTop;
        var sliding = AddPanel(barBg, "SlidingArea", new Vector2(0,0), new Vector2(1,1), new Vector2(5,5), new Vector2(-5,-5), Color.clear);
        var handle = AddPanel(sliding, "Handle", new Vector2(0,0), new Vector2(1,1), Vector2.zero, Vector2.zero, GoldBright);
        slider.handleRect = handle;
        slider.targetGraphic = handle.GetComponent<Image>();
        scroll.verticalScrollbar = slider;
        scroll.verticalScrollbarVisibility = ScrollRect.ScrollbarVisibility.Permanent;
        scroll.verticalScrollbarSpacing = -20;

        // Bottom large mobile action row
        var bottom = AddPanel(root, "BottomBar", new Vector2(0,0), new Vector2(1,0), new Vector2(18,18), new Vector2(-18,120), new Color(0.012f,0.014f,0.018f,0.98f));
        for (int i=0;i<5;i++) AddIconButton(bottom, "Bottom_"+i, i==0 ? GoldBright : Gold, 82, new Vector2(65+i*118,51));
        for (int i=0;i<5;i++) AddRuneSlot(bottom, "Quick_"+i, new Vector2(970+i*118,51), 78, new Color(0.34f,0.28f,0.18f,1), new Color(0.02f,0.02f,0.022f,1));
        AddIconButton(bottom, "Bottom_Action_A", GoldBright, 92, new Vector2(2030,51));
        AddIconButton(bottom, "Bottom_Action_B", GoldBright, 92, new Vector2(2170,51));

        Canvas.ForceUpdateCanvases();
        scroll.verticalNormalizedPosition = 1f;
        Canvas.ForceUpdateCanvases();
    }

    public void SetScroll01(float t)
    {
        if (InventoryScroll == null) return;
        InventoryScroll.verticalNormalizedPosition = Mathf.Clamp01(1f - t);
        Canvas.ForceUpdateCanvases();
    }

    static void EnsureEventSystem()
    {
        if (FindObjectOfType<EventSystem>() != null) return;
        var go = new GameObject("AQ_EventSystem", typeof(EventSystem), typeof(StandaloneInputModule));
        DontDestroyOnLoad(go);
    }

    static RectTransform AddPanel(RectTransform parent, string name, Vector2 amin, Vector2 amax, Vector2 offMin, Vector2 offMax, Color color)
    {
        var go = new GameObject(name, typeof(RectTransform), typeof(Image));
        go.transform.SetParent(parent, false);
        var rt = go.GetComponent<RectTransform>();
        rt.anchorMin = amin; rt.anchorMax = amax; rt.offsetMin = offMin; rt.offsetMax = offMax;
        go.GetComponent<Image>().color = color;
        return rt;
    }

    static void AddLine(RectTransform parent, string name, Vector2 amin, Vector2 amax, Vector2 offMin, Vector2 offMax, Color c)
    {
        AddPanel(parent, name, amin, amax, offMin, offMax, c);
    }

    static void AddBorder(RectTransform rt, Color c, float thickness)
    {
        AddPanel(rt, "BorderTop", new Vector2(0,1), new Vector2(1,1), new Vector2(0,-thickness), Vector2.zero, c);
        AddPanel(rt, "BorderBottom", new Vector2(0,0), new Vector2(1,0), Vector2.zero, new Vector2(0,thickness), c);
        AddPanel(rt, "BorderLeft", new Vector2(0,0), new Vector2(0,1), Vector2.zero, new Vector2(thickness,0), c);
        AddPanel(rt, "BorderRight", new Vector2(1,0), new Vector2(1,1), new Vector2(-thickness,0), Vector2.zero, c);
    }

    static void AddIconButton(RectTransform parent, string name, Color c, float size, Vector2 center)
    {
        var outer = AddPanel(parent, name, new Vector2(0,1), new Vector2(0,1), center - new Vector2(size/2, size/2), center + new Vector2(size/2, size/2), new Color(0.028f,0.029f,0.031f,1));
        outer.pivot = new Vector2(0,1);
        AddBorder(outer, c, 3f);
        var core = AddPanel(outer, "Core", new Vector2(.5f,.5f), new Vector2(.5f,.5f), new Vector2(-10,-10), new Vector2(10,10), c);
        core.localRotation = Quaternion.Euler(0,0,45);
    }

    static void AddRuneSlot(RectTransform parent, string name, Vector2 center, float size, Color border, Color fill)
    {
        var outer = AddPanel(parent, name, new Vector2(0,0), new Vector2(0,0), center - new Vector2(size/2,size/2), center + new Vector2(size/2,size/2), fill);
        AddBorder(outer, border, 5f);
        var mid = AddPanel(outer, "RuneMark", new Vector2(.5f,.5f), new Vector2(.5f,.5f), new Vector2(-17,-17), new Vector2(17,17), border);
        mid.localRotation = Quaternion.Euler(0,0,45);
        var dot = AddPanel(outer, "RuneCore", new Vector2(.5f,.5f), new Vector2(.5f,.5f), new Vector2(-5,-42), new Vector2(5,42), border);
        dot.localRotation = Quaternion.Euler(0,0,45);
    }

    static void AddGearSlot(RectTransform parent, string name, Vector2 center, float size, int idx)
    {
        var slot = AddPanel(parent, name, new Vector2(0,0), new Vector2(0,0), center - new Vector2(size/2,size/2), center + new Vector2(size/2,size/2), new Color(0.024f,0.026f,0.029f,1));
        AddBorder(slot, Gold, 4f);
        AddGlyph(slot, idx, new Color(0.48f,0.46f,0.41f,1));
        for (int i=0;i<2;i++)
        {
            var gem = AddPanel(slot, "Socket_"+i, new Vector2(1,0), new Vector2(1,0), new Vector2(-42+i*22,8), new Vector2(-24+i*22,26), new Color(0.01f,0.01f,0.012f,1));
            AddBorder(gem, GoldBright, 2f);
        }
    }

    static void AddInventorySlot(RectTransform parent, int idx)
    {
        var slot = AddPanel(parent, "Item_"+idx, new Vector2(0,0), new Vector2(0,0), Vector2.zero, new Vector2(148,148), new Color(0.026f,0.028f,0.032f,1));
        AddBorder(slot, idx % 9 == 0 ? new Color(0.50f,0.20f,0.58f,1) : Gold, idx % 9 == 0 ? 4f : 2f);
        AddGlyph(slot, idx, idx % 9 == 0 ? new Color(0.67f,0.31f,0.85f,1) : new Color(0.52f,0.50f,0.45f,1));
    }

    static void AddGlyph(RectTransform parent, int seed, Color c)
    {
        int mode = seed % 5;
        if (mode == 0)
        {
            var g = AddPanel(parent, "Glyph", new Vector2(.5f,.5f), new Vector2(.5f,.5f), new Vector2(-13,-44), new Vector2(13,44), c);
            g.localRotation = Quaternion.Euler(0,0,45);
        }
        else if (mode == 1)
        {
            var g = AddPanel(parent, "Glyph", new Vector2(.5f,.5f), new Vector2(.5f,.5f), new Vector2(-38,-10), new Vector2(38,10), c);
            g.localRotation = Quaternion.Euler(0,0,-35);
        }
        else if (mode == 2)
        {
            AddPanel(parent, "GlyphA", new Vector2(.5f,.5f), new Vector2(.5f,.5f), new Vector2(-30,-8), new Vector2(30,8), c).localRotation = Quaternion.Euler(0,0,45);
            AddPanel(parent, "GlyphB", new Vector2(.5f,.5f), new Vector2(.5f,.5f), new Vector2(-30,-8), new Vector2(30,8), c).localRotation = Quaternion.Euler(0,0,-45);
        }
        else if (mode == 3)
        {
            AddPanel(parent, "GlyphA", new Vector2(.5f,.5f), new Vector2(.5f,.5f), new Vector2(-9,-42), new Vector2(9,42), c);
            AddPanel(parent, "GlyphB", new Vector2(.5f,.5f), new Vector2(.5f,.5f), new Vector2(-36,-8), new Vector2(36,8), c);
        }
        else
        {
            var d = AddPanel(parent, "Glyph", new Vector2(.5f,.5f), new Vector2(.5f,.5f), new Vector2(-26,-26), new Vector2(26,26), c);
            d.localRotation = Quaternion.Euler(0,0,45);
        }
    }

    static void AddRing(RectTransform parent, string name, Vector2 amin, Vector2 amax, Vector2 center, float width, float height, Color c)
    {
        var r = AddPanel(parent, name, amin, amax, center - new Vector2(width/2,height/2), center + new Vector2(width/2,height/2), new Color(0.02f,0.02f,0.022f,1));
        AddBorder(r, c, 4f);
    }

    static void Stretch(RectTransform rt, float xmin, float ymin, float xmax, float ymax, float l, float b, float r, float t)
    {
        rt.anchorMin = new Vector2(xmin,ymin);
        rt.anchorMax = new Vector2(xmax,ymax);
        rt.offsetMin = new Vector2(l,b);
        rt.offsetMax = new Vector2(-r,-t);
    }
}
