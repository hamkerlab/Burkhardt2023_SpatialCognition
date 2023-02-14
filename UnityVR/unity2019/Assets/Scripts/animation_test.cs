/**
@brief Test for a single animation

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using UnityEngine;
using System.Collections;

public class animation_test : MonoBehaviour {
	
	public Transform Cathegory1;
	
	// Use this for initialization
	void Start () {
	
	Instantiate (Cathegory1, new Vector3(2.903169f,2.000727f,1.050051f), Cathegory1 .rotation);	
		
		
	}
	
	// Update is called once per frame
	void Update () {
					
	}
}
