using UnityEngine;

[ExecuteAlways]
public sealed class AQ_VberAISafeAreaFitter : MonoBehaviour
{
    public Vector2 referenceSize = new Vector2(1846f, 852f);
    private Rect _lastSafe;
    private Vector2Int _lastScreen;

    private void OnEnable() { Apply(); }
    private void Update()
    {
        if (_lastSafe != Screen.safeArea || _lastScreen.x != Screen.width || _lastScreen.y != Screen.height)
            Apply();
    }

    public void Apply() { ApplyInternal(Screen.safeArea, Mathf.Max(1, Screen.width), Mathf.Max(1, Screen.height)); }

    public void ApplyForTest(Rect safeAreaPixels, int screenWidth, int screenHeight)
    {
        ApplyInternal(safeAreaPixels, Mathf.Max(1, screenWidth), Mathf.Max(1, screenHeight));
    }

    private void ApplyInternal(Rect safe, int sw, int sh)
    {
        var rt = transform as RectTransform;
        var parent = rt != null ? rt.parent as RectTransform : null;
        if (rt == null || parent == null) return;

        _lastSafe = safe;
        _lastScreen = new Vector2Int(sw, sh);

        rt.anchorMin = rt.anchorMax = new Vector2(0.5f, 0.5f);
        rt.pivot = new Vector2(0.5f, 0.5f);
        rt.sizeDelta = referenceSize;

        Rect pr = parent.rect;
        float nx = safe.x / sw;
        float ny = safe.y / sh;
        float nw = safe.width / sw;
        float nh = safe.height / sh;

        float safeW = pr.width * nw;
        float safeH = pr.height * nh;
        float scale = Mathf.Min(1f, Mathf.Min(safeW / referenceSize.x, safeH / referenceSize.y));
        rt.localScale = new Vector3(scale, scale, 1f);

        float safeCx = (nx + nw * 0.5f - 0.5f) * pr.width;
        float safeCy = (ny + nh * 0.5f - 0.5f) * pr.height;
        rt.anchoredPosition = new Vector2(safeCx, safeCy);
    }
}
