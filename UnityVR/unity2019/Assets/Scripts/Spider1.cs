/**
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using UnityEngine;
using System.Collections;

public class Spider1 : MonoBehaviour {

 void OnTriggerEnter(Collider other) {
		
		if (other.gameObject.name=="Spider"){
			  
			other.transform.Translate(new Vector3(-1f*Time.deltaTime,0,0));
			Debug.Log("234234234");
		}
	}
}
