/**
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using UnityEngine;
using System.Collections;

public class DestroyObject : MonoBehaviour {

	
	void OnTriggerEnter(Collider other) {
		if (other.gameObject.name=="Lerpz"){

			Destroy (gameObject);
			
		}
	}
}
