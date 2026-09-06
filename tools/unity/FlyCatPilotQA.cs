#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

public static class FlyCatPilotQA
{
    [Serializable]
    public class RendererRecord
    {
        public string name;
        public string type;
        public int triangles;
        public int materials;
        public int bones;
        public bool rootBone;
        public bool enabled;
        public bool finiteBounds;
    }

    [Serializable]
    public class Report
    {
        public string status;
        public string unityVersion;
        public string modelAssetPath;
        public int rendererCount;
        public int skinnedRendererCount;
        public int meshRendererCount;
        public int bodyRendererCount;
        public int gearRendererCount;
        public bool allMaterialsNonNull;
        public bool allShadersNonNull;
        public bool gearOnOffIndependent;
        public bool bodyStayedEnabledWhenGearOff;
        public bool proceduralPoseApplied;
        public bool proceduralPoseBakeFinite;
        public string proceduralPoseBone;
        public float bakedBoundsDeltaMagnitude;
        public List<RendererRecord> renderers = new List<RendererRecord>();
        public List<string> warnings = new List<string>();
    }

    static string Arg(string key)
    {
        var args = Environment.GetCommandLineArgs();
        for (int i = 0; i < args.Length - 1; i++)
            if (string.Equals(args[i], key, StringComparison.OrdinalIgnoreCase))
                return args[i + 1];
        return null;
    }

    static bool Finite(float v) => !float.IsNaN(v) && !float.IsInfinity(v);
    static bool Finite(Vector3 v) => Finite(v.x) && Finite(v.y) && Finite(v.z);
    static int Triangles(Mesh m) => m == null ? 0 : m.triangles.Length / 3;

    static bool IsBody(Renderer r)
    {
        var n = r.name.ToLowerInvariant();
        return n.Contains("body_base") || n == "body" || n.Contains("bodyrigged");
    }

    static bool IsGear(Renderer r)
    {
        var n = r.name.ToLowerInvariant();
        return n.Contains("flycat_chest_pilot") || n.Contains("gear_chest") || n.Contains("chest_pilot");
    }

    public static void Run()
    {
        var modelPath = Arg("-flycatModel");
        var reportPath = Arg("-flycatReport");
        if (string.IsNullOrEmpty(modelPath) || string.IsNullOrEmpty(reportPath))
            throw new Exception("Missing -flycatModel or -flycatReport");

        var report = new Report
        {
            status = "STARTED",
            unityVersion = Application.unityVersion,
            modelAssetPath = modelPath
        };

        try
        {
            AssetDatabase.ImportAsset(modelPath, ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(modelPath);
            if (prefab == null) throw new Exception("MODEL_IMPORT_FAILED " + modelPath);
            var go = PrefabUtility.InstantiatePrefab(prefab) as GameObject;
            if (go == null) go = UnityEngine.Object.Instantiate(prefab);
            try
            {
                var renderers = go.GetComponentsInChildren<Renderer>(true);
                report.rendererCount = renderers.Length;
                report.skinnedRendererCount = renderers.OfType<SkinnedMeshRenderer>().Count();
                report.meshRendererCount = renderers.OfType<MeshRenderer>().Count();
                report.bodyRendererCount = renderers.Count(IsBody);
                report.gearRendererCount = renderers.Count(IsGear);
                report.allMaterialsNonNull = true;
                report.allShadersNonNull = true;

                foreach (var r in renderers)
                {
                    Mesh mesh = null;
                    int bones = 0;
                    bool rootBone = false;
                    if (r is SkinnedMeshRenderer smr)
                    {
                        mesh = smr.sharedMesh;
                        bones = smr.bones != null ? smr.bones.Length : 0;
                        rootBone = smr.rootBone != null;
                    }
                    else
                    {
                        var mf = r.GetComponent<MeshFilter>();
                        if (mf != null) mesh = mf.sharedMesh;
                    }
                    var mats = r.sharedMaterials ?? Array.Empty<Material>();
                    if (mats.Any(m => m == null)) report.allMaterialsNonNull = false;
                    if (mats.Any(m => m != null && m.shader == null)) report.allShadersNonNull = false;
                    report.renderers.Add(new RendererRecord
                    {
                        name = r.name,
                        type = r.GetType().Name,
                        triangles = Triangles(mesh),
                        materials = mats.Length,
                        bones = bones,
                        rootBone = rootBone,
                        enabled = r.enabled,
                        finiteBounds = Finite(r.bounds.center) && Finite(r.bounds.size)
                    });
                }

                var bodies = renderers.Where(IsBody).ToArray();
                var gears = renderers.Where(IsGear).ToArray();
                var bodyBefore = bodies.ToDictionary(x => x, x => x.enabled);
                foreach (var g in gears) g.enabled = false;
                report.bodyStayedEnabledWhenGearOff = bodies.Length > 0 && bodies.All(b => b.enabled == bodyBefore[b] && b.enabled);
                report.gearOnOffIndependent = gears.Length > 0 && gears.All(g => !g.enabled) && report.bodyStayedEnabledWhenGearOff;
                foreach (var g in gears) g.enabled = true;

                var gearSmr = gears.OfType<SkinnedMeshRenderer>().FirstOrDefault();
                if (gearSmr == null)
                    gearSmr = go.GetComponentsInChildren<SkinnedMeshRenderer>(true).FirstOrDefault(x => !IsBody(x));
                if (gearSmr != null)
                {
                    var bone = gearSmr.bones.FirstOrDefault(t => t != null &&
                        (t.name.ToLowerInvariant().Contains("spine") || t.name.ToLowerInvariant().Contains("chest")))
                        ?? gearSmr.bones.FirstOrDefault(t => t != null && t.name.ToLowerInvariant().Contains("arm"));
                    if (bone != null)
                    {
                        var tmpA = new Mesh();
                        var tmpB = new Mesh();
                        gearSmr.BakeMesh(tmpA);
                        var beforeSize = tmpA.bounds.size;
                        var oldRot = bone.localRotation;
                        bone.localRotation = oldRot * Quaternion.Euler(12f, 8f, 0f);
                        gearSmr.BakeMesh(tmpB);
                        bone.localRotation = oldRot;
                        report.proceduralPoseApplied = true;
                        report.proceduralPoseBone = bone.name;
                        report.proceduralPoseBakeFinite = tmpB.vertexCount > 0 && Finite(tmpB.bounds.center) && Finite(tmpB.bounds.size);
                        report.bakedBoundsDeltaMagnitude = (tmpB.bounds.size - beforeSize).magnitude;
                        UnityEngine.Object.DestroyImmediate(tmpA);
                        UnityEngine.Object.DestroyImmediate(tmpB);
                    }
                    else report.warnings.Add("No suitable deformation bone found for procedural Unity pose.");
                }
                else report.warnings.Add("No gear SkinnedMeshRenderer found for procedural Unity pose.");

                if (report.bodyRendererCount == 0) report.warnings.Add("BODY_BASE renderer was not found in imported pilot FBX.");
                if (report.gearRendererCount == 0) report.warnings.Add("FLYCAT chest renderer was not found in imported pilot FBX.");
                if (!report.allMaterialsNonNull) report.warnings.Add("At least one renderer has a null material reference.");
                if (!report.allShadersNonNull) report.warnings.Add("At least one imported material has a null shader.");

                bool renderersFinite = report.renderers.All(r => r.finiteBounds);
                report.status = (report.rendererCount > 0 && report.gearRendererCount > 0 &&
                                 report.gearOnOffIndependent && renderersFinite && report.allMaterialsNonNull &&
                                 report.allShadersNonNull && report.proceduralPoseBakeFinite)
                    ? "PASS" : "REVIEW";
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(go);
            }
        }
        catch (Exception ex)
        {
            report.status = "FAIL";
            report.warnings.Add(ex.ToString());
        }

        Directory.CreateDirectory(Path.GetDirectoryName(reportPath));
        File.WriteAllText(reportPath, JsonUtility.ToJson(report, true));
        Debug.Log("FLYCAT_UNITY_QA=" + report.status + " report=" + reportPath);
        if (report.status == "FAIL") EditorApplication.Exit(2);
    }
}
#endif
