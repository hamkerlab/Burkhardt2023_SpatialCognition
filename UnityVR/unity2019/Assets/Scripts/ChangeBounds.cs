/**
@brief Viewfrustum Culling Disabling Workaround
 
@details 
 Unity culls objects automatically. 
 
 Due to the absence of a switch to disable it, the boundingbox of an object has to be enlarged. 
 
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using UnityEngine;

public class ChangeBounds : MonoBehaviour {

	void Start () {
	
	}
	
	// Update is called once per frame
	void Update () {
        float boundwidth = 10000.0f;                    // arbitrary large number
        Mesh mesh = GetComponent<MeshFilter>().mesh;
        mesh.bounds = new Bounds(new Vector3(0, 0, 0), new Vector3(1, 1, 1) * boundwidth);
    }
}
