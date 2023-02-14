/**
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class normal : MonoBehaviour
{
    // Calculate the reflection of a "laser beam" off a clicked object.

    // The object from which the beam is fired. The incoming beam will
    // not be visible if the camera is used for this!
    public Transform Cube;

	// Start is called before the first frame update
    void Start()
    {
        
    }

    void Update()
    {
        if (Input.GetMouseButton(0))
        {
            
			RaycastHit hit;
            Ray ray = Camera.main.ScreenPointToRay(Input.mousePosition);

            if (Physics.Raycast(ray, out hit))
            {
				Debug.Log(hit.normal);
            }
        }
	}
}