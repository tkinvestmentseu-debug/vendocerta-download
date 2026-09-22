using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

public class AetherqorInventoryScrollDemoV2 : MonoBehaviour
{
    public ScrollRect InventoryScroll { get; private set; }
    public RectTransform InventoryContent { get; private set; }
    public RectTransform InventoryViewport { get; private set; }
    public RectTransform Model3DAnchor { get; private set; }

    readonly List<RawImage> slotImages = new();
    RawImage background;
    Texture2D skin;
    static readonly Rect SlotDesignUv = new Rect(
        1237f / 1846f,
        (852f - 184f - 116f) / 852f,
        116f / 1846f,
        116f / 852f
    );
    Rect backgroundUv = new Rect(0,0,1,1);
    Rect slotUv = SlotDesignUv;

    public void BuildNow()
    {
        EnsureEventSystem();

        var camGo = new GameObject("AQ_UI_Camera", typeof(Camera));
        camGo.transform.SetParent(transform, false);
        var cam = camGo.GetComponent<Camera>();
        cam.clearFlags = CameraClearFlags.SolidColor;
        cam.backgroundColor = Color.black;
        cam.orthographic = true;
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
        Stretch(root);

        var bgGo = new GameObject("ApprovedDarkFantasySkin", typeof(RectTransform), typeof(RawImage));
        bgGo.transform.SetParent(root, false);
        Stretch(bgGo.GetComponent<RectTransform>());
        background = bgGo.GetComponent<RawImage>();
        background.raycastTarget = false;

        var model = new GameObject("AETHERQOR_MODEL_3D_ANCHOR", typeof(RectTransform));
        model.transform.SetParent(root, false);
        Model3DAnchor = model.GetComponent<RectTransform>();
        Model3DAnchor.anchorMin = new Vector2(0.285f, 0.12f);
        Model3DAnchor.anchorMax = new Vector2(0.555f, 0.86f);
        Model3DAnchor.offsetMin = Vector2.zero;
        Model3DAnchor.offsetMax = Vector2.zero;

        var hostGo = new GameObject("InventoryScrollHost", typeof(RectTransform), typeof(Image), typeof(ScrollRect));
        hostGo.transform.SetParent(root, false);
        var host = hostGo.GetComponent<RectTransform>();
        host.anchorMin = new Vector2(0.661f, 0.184f);
        host.anchorMax = new Vector2(0.933f, 0.785f);
        host.offsetMin = Vector2.zero;
        host.offsetMax = Vector2.zero;
        hostGo.GetComponent<Image>().color = new Color(0.008f, 0.009f, 0.011f, 1f);

        var vpGo = new GameObject("Viewport", typeof(RectTransform), typeof(Image), typeof(RectMask2D));
        vpGo.transform.SetParent(host, false);
        var vp = vpGo.GetComponent<RectTransform>();
        Stretch(vp);
        vpGo.GetComponent<Image>().color = new Color(0.008f, 0.009f, 0.011f, 1f);
        InventoryViewport = vp;

        var contentGo = new GameObject("Content", typeof(RectTransform), typeof(GridLayoutGroup), typeof(ContentSizeFitter));
        contentGo.transform.SetParent(vp, false);
        var content = contentGo.GetComponent<RectTransform>();
        content.anchorMin = new Vector2(0, 1);
        content.anchorMax = new Vector2(1, 1);
        content.pivot = new Vector2(0.5f, 1);
        content.anchoredPosition = Vector2.zero;
        content.sizeDelta = Vector2.zero;
        InventoryContent = content;

        var grid = contentGo.GetComponent<GridLayoutGroup>();
        grid.padding = new RectOffset(8, 8, 8, 8);
        grid.cellSize = new Vector2(142, 142);
        grid.spacing = new Vector2(12, 12);
        grid.constraint = GridLayoutGroup.Constraint.FixedColumnCount;
        grid.constraintCount = 4;
        grid.startCorner = GridLayoutGroup.Corner.UpperLeft;
        grid.startAxis = GridLayoutGroup.Axis.Horizontal;
        grid.childAlignment = TextAnchor.UpperLeft;

        var fitter = contentGo.GetComponent<ContentSizeFitter>();
        fitter.horizontalFit = ContentSizeFitter.FitMode.Unconstrained;
        fitter.verticalFit = ContentSizeFitter.FitMode.PreferredSize;

        for (int i = 0; i < 48; i++) AddEmptySlot(content, i);

        var scroll = hostGo.GetComponent<ScrollRect>();
        scroll.content = content;
        scroll.viewport = vp;
        scroll.horizontal = false;
        scroll.vertical = true;
        scroll.inertia = true;
        scroll.decelerationRate = 0.12f;
        scroll.scrollSensitivity = 70f;
        scroll.movementType = ScrollRect.MovementType.Clamped;
        InventoryScroll = scroll;

        BuildScrollbar(root, scroll);
        Canvas.ForceUpdateCanvases();
        LayoutRebuilder.ForceRebuildLayoutImmediate(content);
        SetScroll01(0);
    }

    public void ApplySkin(Texture2D texture)
    {
        skin = texture;
        backgroundUv = CenterCropUv(texture.width, texture.height, 13f / 6f);
        slotUv = MapDesignUvIntoTexture(SlotDesignUv, backgroundUv);
        background.texture = texture;
        background.uvRect = backgroundUv;
        foreach (var slot in slotImages)
        {
            slot.texture = texture;
            slot.uvRect = slotUv;
        }
    }

    public void SetScroll01(float t)
    {
        if (InventoryContent == null || InventoryViewport == null) return;
        Canvas.ForceUpdateCanvases();
        LayoutRebuilder.ForceRebuildLayoutImmediate(InventoryContent);
        float maxTravel = Mathf.Max(0, InventoryContent.rect.height - InventoryViewport.rect.height);
        var p = InventoryContent.anchoredPosition;
        p.y = Mathf.Clamp01(t) * maxTravel;
        InventoryContent.anchoredPosition = p;
        InventoryScroll.verticalNormalizedPosition = 1f - Mathf.Clamp01(t);
        Canvas.ForceUpdateCanvases();
    }

    void AddEmptySlot(RectTransform parent, int i)
    {
        var go = new GameObject("EmptySlot_" + i, typeof(RectTransform), typeof(RawImage));
        go.transform.SetParent(parent, false);
        var raw = go.GetComponent<RawImage>();
        raw.color = Color.white;
        raw.raycastTarget = true;
        raw.uvRect = slotUv;
        raw.texture = skin;
        slotImages.Add(raw);
    }

    static void BuildScrollbar(RectTransform root, ScrollRect scroll)
    {
        var tgo = new GameObject("RealScrollbarTrack", typeof(RectTransform), typeof(Image), typeof(Scrollbar));
        tgo.transform.SetParent(root, false);
        var tr = tgo.GetComponent<RectTransform>();
        tr.anchorMin = new Vector2(0.955f, 0.194f);
        tr.anchorMax = new Vector2(0.968f, 0.778f);
        tr.offsetMin = tr.offsetMax = Vector2.zero;
        tgo.GetComponent<Image>().color = new Color(0.022f, 0.018f, 0.012f, 1f);

        var lineGo = new GameObject("GoldTrack", typeof(RectTransform), typeof(Image));
        lineGo.transform.SetParent(tr, false);
        var line = lineGo.GetComponent<RectTransform>();
        line.anchorMin = new Vector2(0.43f, 0.02f);
        line.anchorMax = new Vector2(0.57f, 0.98f);
        line.offsetMin = line.offsetMax = Vector2.zero;
        lineGo.GetComponent<Image>().color = new Color(0.50f, 0.36f, 0.17f, 1f);

        var slideGo = new GameObject("SlidingArea", typeof(RectTransform));
        slideGo.transform.SetParent(tr, false);
        var slide = slideGo.GetComponent<RectTransform>();
        slide.anchorMin = Vector2.zero;
        slide.anchorMax = Vector2.one;
        slide.offsetMin = new Vector2(2, 10);
        slide.offsetMax = new Vector2(-2, -10);

        var hgo = new GameObject("Handle", typeof(RectTransform), typeof(Image));
        hgo.transform.SetParent(slide, false);
        var h = hgo.GetComponent<RectTransform>();
        h.anchorMin = new Vector2(0, 0);
        h.anchorMax = new Vector2(1, 0.18f);
        h.offsetMin = h.offsetMax = Vector2.zero;
        hgo.GetComponent<Image>().color = new Color(0.84f, 0.63f, 0.29f, 1f);

        var bar = tgo.GetComponent<Scrollbar>();
        bar.direction = Scrollbar.Direction.BottomToTop;
        bar.handleRect = h;
        bar.targetGraphic = hgo.GetComponent<Image>();
        scroll.verticalScrollbar = bar;
        scroll.verticalScrollbarVisibility = ScrollRect.ScrollbarVisibility.Permanent;
    }

    static Rect CenterCropUv(int width, int height, float targetAspect)
    {
        float sourceAspect = width / (float)height;
        if (Mathf.Abs(sourceAspect - targetAspect) < 0.0001f) return new Rect(0,0,1,1);
        if (sourceAspect < targetAspect)
        {
            float visibleHeight = sourceAspect / targetAspect;
            float y = (1f - visibleHeight) * 0.5f;
            return new Rect(0f, y, 1f, visibleHeight);
        }
        float visibleWidth = targetAspect / sourceAspect;
        float x = (1f - visibleWidth) * 0.5f;
        return new Rect(x, 0f, visibleWidth, 1f);
    }

    static Rect MapDesignUvIntoTexture(Rect designUv, Rect bgUv)
    {
        return new Rect(
            bgUv.x + designUv.x * bgUv.width,
            bgUv.y + designUv.y * bgUv.height,
            designUv.width * bgUv.width,
            designUv.height * bgUv.height
        );
    }

    static void EnsureEventSystem()
    {
        if (FindObjectOfType<EventSystem>() != null) return;
        var go = new GameObject("AQ_EventSystem", typeof(EventSystem), typeof(StandaloneInputModule));
        if (Application.isPlaying) DontDestroyOnLoad(go);
    }

    static void Stretch(RectTransform rt)
    {
        rt.anchorMin = Vector2.zero;
        rt.anchorMax = Vector2.one;
        rt.offsetMin = Vector2.zero;
        rt.offsetMax = Vector2.zero;
    }
}
