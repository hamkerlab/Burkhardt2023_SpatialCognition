/**
@brief Simple comparison of projections
 
@details 
  This class saves screenshots of different perspectives for each projection.
  Currently, there is only a simple, lighted cube in the scene.
  
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using System.IO;
using UnityEngine;

class SimplePerspectiveBehaviourScript : MonoBehaviour
{
    RenderTexture rt, srt;
    Texture2D tex, stex;
    Camera tempcam;
    // fixed rendering properties, independent of editor settings
    const int imgWidth = 1024;
    int imgHeight, sImgHeight;
    const float fovH = 90;
    const float fovV = 60;

    Shader shader1;
    Shader shader2;

    // Function is called immediatly after the scene starts running.
    /// <summary>
    /// Creates new cameras, with certain positions and orientations which are defined here
    /// Currently the camera is facing the cube in three different ways - each way with different distances.
    /// </summary>
    void Start() {
        GameObject temp = GameObject.Find("TemplateCamera");
        this.tempcam = temp.GetComponent<Camera>();
        imgHeight = Mathf.RoundToInt(imgWidth * Mathf.Tan(Mathf.Deg2Rad * fovV / 2.0f) / Mathf.Tan(Mathf.Deg2Rad * fovH / 2.0f));
        sImgHeight = (int)(imgWidth * fovV / fovH);
        tex = new Texture2D(imgWidth, imgHeight, TextureFormat.RGB24, false);
        stex = new Texture2D(imgWidth, sImgHeight, TextureFormat.RGB24, false);
        rt = new RenderTexture(imgWidth, imgHeight, 24);
        srt = new RenderTexture(imgWidth, sImgHeight, 24);

        shader1 = Shader.Find("Diffuse");
        shader2 = Shader.Find("SphericalProjectionLit");

        Directory.CreateDirectory(Application.dataPath + "/../../../Screenshots");

        Vector3 pos = new Vector3(0,0,0);
        Quaternion rot = new Quaternion();

        // ============== Z-Axis / One Face to Camera ===================

        pos.Set(0,0,-2);
        Vector3 look1 = new Vector3(0, 0, 0) - pos,
            look2 = new Vector3(0.5f, 0, 0) - pos,
            look3 = new Vector3(1, 0, 0) - pos,
            look4 = new Vector3(1.5f, 0, 0) - pos;
        
        rot.SetLookRotation(look1);
        newCamAndPic(pos, rot);
        rot.SetLookRotation(look2);
        newCamAndPic(pos, rot);
        rot.SetLookRotation(look3);
        newCamAndPic(pos, rot);
        rot.SetLookRotation(look4);
        newCamAndPic(pos, rot);

        pos.Set(0, 0, -3);

        rot.SetLookRotation(look1);
        newCamAndPic(pos, rot);
        rot.SetLookRotation(look2);
        newCamAndPic(pos, rot);
        rot.SetLookRotation(look3);
        newCamAndPic(pos, rot);
        rot.SetLookRotation(look4);
        newCamAndPic(pos, rot);

        pos.Set(0, 0, -4);

        rot.SetLookRotation(look1);
        newCamAndPic(pos, rot);
        rot.SetLookRotation(look2);
        newCamAndPic(pos, rot);
        rot.SetLookRotation(look3);
        newCamAndPic(pos, rot);
        rot.SetLookRotation(look4);
        newCamAndPic(pos, rot);

        pos.Set(0, 0, -5);

        rot.SetLookRotation(look1);
        newCamAndPic(pos, rot);
        rot.SetLookRotation(look2);
        newCamAndPic(pos, rot);
        rot.SetLookRotation(look3);
        newCamAndPic(pos, rot);
        rot.SetLookRotation(look4);
        newCamAndPic(pos, rot);
        
        // ============== One Edge to Camera ===================

        float d = Mathf.Sqrt(2);
        Quaternion r = Quaternion.Euler(0, 45.0f, 0);
        pos.Set(-d, 0,-d);
        
        rot.SetLookRotation(look1);
        newCamAndPic(pos, r * rot);
        rot.SetLookRotation(look2);
        newCamAndPic(pos, r * rot);
        rot.SetLookRotation(look3);
        newCamAndPic(pos, r * rot);
        rot.SetLookRotation(look4);
        newCamAndPic(pos, r * rot);

        pos.Set(-d * 1.5f, 0, -d * 1.5f);

        rot.SetLookRotation(look1);
        newCamAndPic(pos, r * rot);
        rot.SetLookRotation(look2);
        newCamAndPic(pos, r * rot);
        rot.SetLookRotation(look3);
        newCamAndPic(pos, r * rot);
        rot.SetLookRotation(look4);
        newCamAndPic(pos, r * rot);

        pos.Set(-d * 2.0f, 0, -d * 2.0f);

        rot.SetLookRotation(look1);
        newCamAndPic(pos, r * rot);
        rot.SetLookRotation(look2);
        newCamAndPic(pos, r * rot);
        rot.SetLookRotation(look3);
        newCamAndPic(pos, r * rot);
        rot.SetLookRotation(look4);
        newCamAndPic(pos, r * rot);

        pos.Set(-d * 2.5f, 0, -d * 2.5f);

        rot.SetLookRotation(look1);
        newCamAndPic(pos, r * rot);
        rot.SetLookRotation(look2);
        newCamAndPic(pos, r * rot);
        rot.SetLookRotation(look3);
        newCamAndPic(pos, r * rot);
        rot.SetLookRotation(look4);
        newCamAndPic(pos, r * rot);
        
        // ============== One Vertex to Camera ===================

        d = Mathf.Sqrt(2.0f*2.0f / 3.0f);
        Quaternion s = Quaternion.Euler(45.0f, 0, 0);
        pos.Set(-d, d, -d);

        rot.SetLookRotation(look1);
        newCamAndPic(pos, r * s * rot);
        rot.SetLookRotation(look2);
        newCamAndPic(pos, r * s * rot);
        rot.SetLookRotation(look3);
        newCamAndPic(pos, r * s * rot);
        rot.SetLookRotation(look4);
        newCamAndPic(pos, r * s * rot);

        pos.Set(-d * 1.5f, d * 1.5f, -d * 1.5f);

        rot.SetLookRotation(look1);
        newCamAndPic(pos, r * s * rot);
        rot.SetLookRotation(look2);
        newCamAndPic(pos, r * s * rot);
        rot.SetLookRotation(look3);
        newCamAndPic(pos, r * s * rot);
        rot.SetLookRotation(look4);
        newCamAndPic(pos, r * s * rot);

        pos.Set(-d * 2.0f, d * 2.0f, -d * 2.0f);

        rot.SetLookRotation(look1);
        newCamAndPic(pos, r * s * rot);
        rot.SetLookRotation(look2);
        newCamAndPic(pos, r * s * rot);
        rot.SetLookRotation(look3);
        newCamAndPic(pos, r * s * rot);
        rot.SetLookRotation(look4);
        newCamAndPic(pos, r * s * rot);

        pos.Set(-d * 2.5f, d * 2.5f, -d * 2.5f);

        rot.SetLookRotation(look1);
        newCamAndPic(pos, r * s * rot);
        rot.SetLookRotation(look2);
        newCamAndPic(pos, r * s * rot);
        rot.SetLookRotation(look3);
        newCamAndPic(pos, r * s * rot);
        rot.SetLookRotation(look4);
        newCamAndPic(pos, r * s * rot);
    }

    /// <summary>
    /// Instantiating new camera with Position and saves screenshot for each projection.
    /// </summary>
    /// <param name="pos">Camera position</param>
    /// <param name="rot">Camera rotation</param>
    void newCamAndPic(Vector3 pos, Quaternion rot) {
        Camera cam = Instantiate(tempcam, pos, rot) as Camera;

        // Perspective Projection
        cam.targetTexture = rt;
        cam.Render();
        RenderTexture.active = rt;
        tex.ReadPixels(new Rect(0, 0, imgWidth, imgHeight), 0, 0);
        tex.Apply();
        File.WriteAllBytes(Application.dataPath + "/../../../Screenshots/P" + pos.ToString() + "_" + rot.ToString() + ".png", tex.EncodeToPNG());

        // Spherical Projection
            // for custom projections, shader have to changed
        MeshRenderer[] mr = (MeshRenderer[])Resources.FindObjectsOfTypeAll(typeof(MeshRenderer));
        foreach (MeshRenderer r in mr) {
            foreach (Material m in r.materials) {
                // material and texture should not be changed
                m.shader = shader2;
                m.SetFloat("_FoVV", fovV);
                m.SetFloat("_Aspect", fovH/fovV);
                m.SetFloat("_F", cam.farClipPlane);
                m.SetFloat("_N", cam.nearClipPlane);
            }
        }
        cam.targetTexture = srt;
        cam.Render();
        RenderTexture.active = srt;
        stex.ReadPixels(new Rect(0, 0, imgWidth, sImgHeight), 0, 0);
        stex.Apply();
        File.WriteAllBytes(Application.dataPath + "/../../../Screenshots/S" + pos.ToString() + "_" + rot.ToString() + ".png", stex.EncodeToPNG());
        foreach (MeshRenderer r in mr)
        {
            foreach (Material m in r.materials)
            {
                // material and texture should not be changed
                m.shader = shader1;
            }
        }

        // Orthogonal Projection
        cam.orthographic = true;
        cam.orthographicSize = 2;
        cam.targetTexture = rt;
        cam.Render();
        RenderTexture.active = rt;
        tex.ReadPixels(new Rect(0, 0, imgWidth, imgHeight), 0, 0);
        tex.Apply();
        File.WriteAllBytes(Application.dataPath + "/../../../Screenshots/O" + pos.ToString() + "_" + rot.ToString() + ".png", tex.EncodeToPNG());
    }
}

