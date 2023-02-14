/**
@brief Saves evaluation data for perspective distortion comparison between perspective and spherical projection
 
@details 
  With key presses, data is saved and compared and screenshots are saved.
  Currently, script is specific for PerspectiveLaboritory scene. 
  Screenshots and Evaluationdata is saved with an Index which increases with every press on V/v (Reference Data ideally: 0).
  
  V/v: Gather Data and save Screenshots
  B/b: Save as reference
  C/c: Compare with reference and save
 
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using UnityEngine;
using System;
using System.IO;
using System.Collections.Generic;

using XMLSerializer;

public class VertexDistortionCheck : MonoBehaviour {
    
    /// <summary>
	/// Used camera.
	/// </summary>
    public Camera cam;
    /// <summary>
	/// Object of interest.
	/// </summary>
    public GameObject obj;

    // helping members
    GameObject objClone;
    Shader sphericalShader;
    bool secondFrame;
    ProjEvaluation xmlContainer;
    int index;
    Component[] mf;

    void Start () {
        index = 0;
        secondFrame = false;
        Directory.CreateDirectory(Path.Combine(Application.dataPath, "../Evaluation"));

        sphericalShader = Shader.Find("SphericalProjectionLit");

        objClone = Instantiate(obj, new Vector3(obj.transform.position.x, obj.transform.position.y,
            obj.transform.position.z), obj.transform.rotation) as GameObject;
        Component[] mr = objClone.GetComponentsInChildren(typeof(MeshRenderer));

        foreach (MeshRenderer r in mr)
        {
            foreach (Material m in r.materials)
            {
                m.shader = sphericalShader;
                m.SetFloat("_FoVV", cam.fieldOfView);
                m.SetFloat("_Aspect", cam.aspect);
                m.SetFloat("_F", cam.farClipPlane);
                m.SetFloat("_N", cam.nearClipPlane);
            }
        }

        //objClone.SetActive(false);

        mf = obj.GetComponentsInChildren(typeof(MeshFilter));
    }
	
	void Update () {
        // Simple way to save screenshots does not allow changes between them.
        if (secondFrame)
        {
            MakeScreenShots(false);
            secondFrame = false;
        }
        else
        {
            obj.SetActive(true);
            objClone.SetActive(false);
        }
        // Press V/v for gathering evaluation data and save one screenshot for each projection.
        if (Input.GetKeyUp(KeyCode.V))
        {
            GatherProjectionData(obj);
            MakeScreenShots(true);
            secondFrame = true;
            Debug.Log("Gathered Data:" + index);
            ++index;
        }
        // Store gathered data as reference data.
        if (Input.GetKeyUp(KeyCode.B))
        {
            xmlContainer.Save(Path.Combine(Application.dataPath, "../Evaluation/RefData.xml"));
            Debug.Log("Saved RefData");
        }
        // Compare gathered data with reference data and store it as evaluation results.
        if (Input.GetKeyUp(KeyCode.C))
        {
            ProjEvaluation compData = ProjEvaluation.Load(Path.Combine(Application.dataPath, "../Evaluation/RefData.xml"));
            DistortionCheck(compData);
            xmlContainer.Save(Path.Combine(Application.dataPath, "../Evaluation/" + (index - 1) + "EvaData.xml"));
            Debug.Log("Saved EvaData" + (index - 1));
        }
        // Disable culling workaround
        foreach (MeshFilter f in mf)
        {
            Mesh mesh = f.mesh;
            mesh.bounds = new Bounds(new Vector3(0, 0, 0), new Vector3(1, 1, 1) * 1000.0f);
        }
    }

    /// <summary>
    /// Compares gathered data with reference data.
    /// Compares distances of vertex to the reference vertex of a mesh
    /// for each projection and saves the maximum and the mean deviation.
    /// </summary>
    /// <param name="refData">Reference data</param>
    void DistortionCheck(ProjEvaluation refData)
    {
        for (int i = 1; i < xmlContainer.Vertices.Count; ++i)
        {
            float oldDistP = refData.Vertices[i].PerspectiveDistanceToV0;
            float oldDistS = refData.Vertices[i].SphericalDistanceToV0;

            if (oldDistS != 0.0f)
            {
                float newDistS = xmlContainer.Vertices[i].SphericalDistanceToV0;
                float dS = Mathf.Abs(newDistS / oldDistS - 1.0f);
                xmlContainer.Vertices[i].SphericalDistortion = dS;

                if (dS > xmlContainer.maxDS)
                    xmlContainer.maxDS = dS;
                xmlContainer.meanDS += dS;
            }

            if (oldDistP != 0.0f)
            {
                float newDistP = xmlContainer.Vertices[i].PerspectiveDistanceToV0;
                float dP = Mathf.Abs(newDistP / oldDistP - 1.0f);
                xmlContainer.Vertices[i].PerspectiveDistortion = dP;
                if (dP > xmlContainer.maxDP)
                    xmlContainer.maxDP = dP;
                xmlContainer.meanDP += dP;
            }
        }
        xmlContainer.meanDP /= (float)(xmlContainer.Vertices.Count - 1);
        xmlContainer.meanDS /= (float)(xmlContainer.Vertices.Count - 1);
    }

    /// <summary>
    /// Stores camera information and vertex data 
    /// along the transformation pipeline in a container for XML export.
    /// </summary>
    void GatherProjectionData(GameObject obj)
    {
        xmlContainer = new ProjEvaluation();
        xmlContainer.verticalFoV = cam.fieldOfView;
        xmlContainer.imgWidth = cam.pixelWidth;
        xmlContainer.imgHeight = cam.pixelHeight;
        xmlContainer.n = cam.nearClipPlane;
        xmlContainer.f = cam.farClipPlane;
        xmlContainer.maxDP = xmlContainer.maxDS = xmlContainer.meanDP = xmlContainer.meanDS = 0;

        //Vector3[] vertices = obj.GetComponent<MeshFilter>().mesh.vertices;        //Objects with no children
        Vector3[] vertices = GetVerticesInChildren(obj);                            //Objects with children
        xmlContainer.VCount = vertices.Length;

        for (int i = 0; i < vertices.Length; ++i)
        {
            Vertex v = new Vertex();
            v.index = i;
            v.PerspectiveDistortion = 0;
            v.SphericalDistortion = 0;

            Vector4 vertex = vertices[i];
            vertex.w = 1;
            ComparePipelineResults(vertex, ref cam, ref obj, ref v);

            xmlContainer.Vertices.Add(v);

            xmlContainer.Vertices[i].PerspectiveDistanceToV0 = Vector2.Distance(
                xmlContainer.Vertices[0].vp(), xmlContainer.Vertices[i].vp());
            xmlContainer.Vertices[i].SphericalDistanceToV0 = Vector2.Distance(
                xmlContainer.Vertices[0].vs(), xmlContainer.Vertices[i].vs());

        }
        
    }

    /// <summary>
    /// Transforms a single vertex along the transformation pipeline.
    /// It is projected seperatly for spherical and perspective projection.
    /// The results are image coordinates with assumed origin in the screen origin.
    /// </summary>
    /// <param name="vertex">The current vertex.</param>
    /// <param name="cam">Reference to the used camera.</param>
    /// <param name="obj">Reference to the analyzed object.</param>
    /// <param name="xmlV">Reference to member of a class for XML export.</param>
    void ComparePipelineResults(Vector4 vertex, ref Camera cam, ref GameObject obj, ref Vertex xmlV)
    {
        // ------------------- Object -> World -> Eye --------------------
        Matrix4x4 M = Matrix4x4.TRS(obj.transform.position, obj.transform.rotation, obj.transform.localScale);
        Vector4 world = M * vertex;

        xmlV.WorldSpace.x = world.x;
        xmlV.WorldSpace.y = world.y;
        xmlV.WorldSpace.z = world.z;

        Matrix4x4 V, R, T;
        Vector3 f = (cam.transform.rotation * Vector3.forward).normalized;
        Vector3 up = (cam.transform.rotation * Vector3.up).normalized;
        Vector3 s = Vector3.Cross(f, up).normalized;
        Vector3 u = Vector3.Cross(s, f);
        T = Matrix4x4.TRS(-cam.transform.position, Quaternion.identity, new Vector3(1, 1, 1));
        R = Matrix4x4.identity;
        R.m00 = s.x; R.m01 = s.y; R.m02 = s.z;
        R.m10 = u.x; R.m11 = u.y; R.m12 = u.z;
        R.m20 = -f.x; R.m21 = -f.y; R.m22 = -f.z;
        V = R * T;

        Vector4 eye = V * world;

        xmlV.EyeSpace.x = eye.x;
        xmlV.EyeSpace.y = eye.y;
        xmlV.EyeSpace.z = eye.z;

        // ------------------- Perspective -------------------------------
        //cam.camera.ResetProjectionMatrix();
        Vector4 clip = cam.GetComponent<Camera>().projectionMatrix * eye;

        Vector4 ndc = clip / clip.w;

        xmlV.NDCofPerspective.x = ndc.x;
        xmlV.NDCofPerspective.y = ndc.y;

        // ------------------- Spherical ---------------------------------

        const float PI = 3.14159f;
        float phi = cam.fieldOfView * PI / 360.0f;
        float theta = phi * cam.aspect;

        float d = Vector3.Distance(Vector3.zero, eye);

        float polar = Mathf.Asin(eye.y / d);
        theta /= Mathf.Cos(polar);
        Vector4 res;
        res.x = (float)Math.Asin(eye.x / (Mathf.Cos(polar) * d)) / theta;
        res.y = polar / phi;
        res.z = (d - 0.3f) / (1000.0f - 0.3f);
        if (res.z <= 0.0f)
            res.z = -0.0001f;
        else
            res.z = -Mathf.Sign(eye.z) * res.z;

        res.w = 1;

        xmlV.NDCofSpherical.x = res.x;
        xmlV.NDCofSpherical.y = res.y;

        // ------------------- Viewport ----------------------------------
        Vector2 PRes = new Vector2(), SRes= new Vector2();
        //assume x_min and y_min in (0,0) of screen
        PRes.x = cam.pixelWidth / 2.0f * (-ndc.x) + cam.pixelWidth / 2.0f;
        SRes.x = cam.pixelWidth / 2.0f * (-res.x) + cam.pixelWidth / 2.0f;

        PRes.y = cam.pixelHeight / 2.0f * ndc.y + cam.pixelHeight / 2.0f;
        SRes.y = cam.pixelHeight / 2.0f * res.y + cam.pixelHeight / 2.0f;

        xmlV.PerspectiveImageCoord.x = PRes.x;
        xmlV.PerspectiveImageCoord.y = PRes.y;

        xmlV.SphericalImageCoord.x = SRes.x;
        xmlV.SphericalImageCoord.y = SRes.y;
    }

    /// <summary>
    /// Saves screenshots for both Projections in two consecutive frames.
    /// </summary>
    void MakeScreenShots(bool first)
    {
        if (first)
        {
            ScreenCapture.CaptureScreenshot("Evaluation/" + index + "Persp.png");
            return;
        }
        obj.SetActive(false);
        objClone.SetActive(true);
        ScreenCapture.CaptureScreenshot("Evaluation/" + (index - 1) + "Spherical.png");
    }
    
    Vector3[] GetVerticesInChildren(GameObject go)
    {
        MeshFilter[] mfs = go.GetComponentsInChildren<MeshFilter>();
        List<Vector3> vList = new List<Vector3>();
        foreach (MeshFilter mf in mfs)
        {
            vList.AddRange(mf.mesh.vertices);
        }
        return vList.ToArray();
    }
}
