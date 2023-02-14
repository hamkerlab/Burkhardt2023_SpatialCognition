/**
@brief Experimental class for projection changes.

@details
 Clones a collection of objects in the scene.
 Shaders of clones are changed.
 Switch between displaying clone room and original by pressing H/h.
 
 Script is currently limited to PerspectiveLaboritory scene and the "Testroom1" object.  

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using UnityEngine;

public class PerspectiveLaboratoryBehaviorScript : MonoBehaviour
{

    public bool sphericalProj = false;
    Shader sphericalShader;
    Camera cam;
    Component[] mr;
    Component[] mf;
    Component[] smr;
    GameObject room;
    GameObject cloneRoom;
    public float boundWidth = 10000.0f;

    void Start()
    {
        this.cam = GameObject.Find("FreeCamera").GetComponent<Camera>();

        this.sphericalShader = Shader.Find("SphericalProjectionLit");
        this.room = GameObject.Find("Testroom1");
        this.cloneRoom = Instantiate(this.room) as GameObject;

        this.mr = this.cloneRoom.GetComponentsInChildren(typeof(MeshRenderer));
        this.smr = this.cloneRoom.GetComponentsInChildren(typeof(SkinnedMeshRenderer));
        this.mf = this.cloneRoom.GetComponentsInChildren(typeof(MeshFilter));

        foreach (MeshRenderer r in this.mr)
        {
            foreach (Material m in r.materials)
            {
                // material and texture should not be changed
                    //Color col = m.GetColor("_Color");
                    //Texture tex = m.GetTexture("_MainTex");
                    //Vector2 offset = m.GetTextureOffset("_MainTex");
                    //m.SetTexture("_MainTex", tex);
                    //m.SetTextureOffset("_MainTex", offset);
                m.shader = this.sphericalShader;
                m.SetFloat("_FoVV", cam.fieldOfView);
                m.SetFloat("_Aspect", cam.aspect);
                m.SetFloat("_F", cam.farClipPlane);
                m.SetFloat("_N", cam.nearClipPlane);
                
            }
            //r.bounds.SetMinMax(new Vector3(-1,-1,-1) * boundWidth, new Vector3(1,1,1) * boundWidth);      // desirable but doesn't work
        }

        foreach (SkinnedMeshRenderer r in this.smr)
        {
            foreach (Material m in r.materials)
            {
                // material and texture should not be changed
                    //Color col = m.GetColor("_Color");
                    //Texture tex = m.GetTexture("_MainTex");
                    //Vector2 offset = m.GetTextureOffset("_MainTex");
                    //m.SetTexture("_MainTex", tex);
                    //m.SetTextureOffset("_MainTex", offset);
                m.shader = this.sphericalShader;
                m.SetFloat("_FoVV", cam.fieldOfView);
                m.SetFloat("_Aspect", cam.aspect);
                m.SetFloat("_F", cam.farClipPlane);
                m.SetFloat("_N", cam.nearClipPlane);
            }
            //r.bounds.SetMinMax(new Vector3(-1, -1, -1) * boundWidth, new Vector3(1, 1, 1) * boundWidth);  // desirable but doesn't work
        }

        if (this.sphericalProj)
            changeShaderToSpherical();
        else
            changeShaderToDefault();

        //Debug.Log(GameObject.Find("Ceiling").name)                            <- works
        //Debug.Log(GameObject.Find("Testroom1/Ceiling").name)                  <- doesn't work
        //Debug.Log(GameObject.Find("Testroom1/Boundaries/Ceiling").name);      <- works
    }

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.H))
        {
            if (this.sphericalProj)
                changeShaderToDefault();
            else
                changeShaderToSpherical();

            this.sphericalProj = !sphericalProj;
        }

        // enlarge boundingboxes -> View Frustum Culling Workaround
        if (this.sphericalProj)
            foreach (MeshFilter f in this.mf) {
                Mesh mesh = f.mesh;
                mesh.bounds = new Bounds(new Vector3(0, 0, 0), new Vector3(1, 1, 1) * boundWidth);
            }
        /*
            foreach (SkinnedMeshRenderer r in this.smr)
            {
                r.sharedMesh.bounds = new Bounds(new Vector3(0, 0, 0), new Vector3(1, 1, 1) * boundWidth);
            }
            // change of boundingsboxes of skinned mesh renderer seems not to work
        */
    }

    void changeShaderToSpherical()
    {
        this.room.SetActive(false);
        this.cloneRoom.SetActive(true);
    }
    void changeShaderToDefault()
    {
        this.room.SetActive(true);
        this.cloneRoom.SetActive(false);
    }
}
