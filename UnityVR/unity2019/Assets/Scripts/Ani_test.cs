/**
@brief Test for grasping animations

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using UnityEngine;
using System.Collections;

public class Ani_test : MonoBehaviour {

	// Use this for initialization
	void Start () {
	
	}
	
	// Update is called once per frame
	void Update () {
	
		if (Input.GetKey (KeyCode.Y))
			//gameObject.animation.Play ("0_1");
			gameObject.GetComponent<Animation>().Play ("PY1_1");
		
		if (Input.GetKey (KeyCode.X))
			//gameObject.animation.Play ("0_2");
			gameObject.GetComponent<Animation>().Play ("P0_2");
		
		if (Input.GetKey (KeyCode.C))
			//gameObject.animation.Play ("0_3");
			gameObject.GetComponent<Animation>().Play ("PX1_1");
		
		if (Input.GetKey (KeyCode.V))
			//gameObject.animation.Play ("X0_1");
			gameObject.GetComponent<Animation>().Play ("PX1_2");
		
		if (Input.GetKey (KeyCode.B))
			//gameObject.animation.Play ("X0_2");
			gameObject.GetComponent<Animation>().Play ("px0_2");
		
		if (Input.GetKey (KeyCode.N))
			gameObject.GetComponent<Animation>().Play ("X0_3");
		
		if (Input.GetKey (KeyCode.I))
			gameObject.GetComponent<Animation>().Play ("X1_1");
		
		if (Input.GetKey (KeyCode.U))
			gameObject.GetComponent<Animation>().Play ("X1_2");
		
		if (Input.GetKey (KeyCode.F))
			gameObject.GetComponent<Animation>().Play ("X1_3");
		
		if (Input.GetKey (KeyCode.P))
			gameObject.GetComponent<Animation>().Play ("X2_2");
		
		if (Input.GetKey (KeyCode.O))
			gameObject.GetComponent<Animation>().Play ("X3_1");
		
		if (Input.GetKey (KeyCode.L))
			gameObject.GetComponent<Animation>().Play ("Y0_1");
		
		if (Input.GetKey (KeyCode.K))
			gameObject.GetComponent<Animation>().Play ("Y0_2");
		
		if (Input.GetKey (KeyCode.J))
			gameObject.GetComponent<Animation>().Play ("Y1_1");
		
		if (Input.GetKey (KeyCode.H))
			gameObject.GetComponent<Animation>().Play ("Y1_2");
		
		if (Input.GetKey (KeyCode.G))
			gameObject.GetComponent<Animation>().Play ("Y2_1");
		
		if (Input.GetKey (KeyCode.M)) {
			//float vertical=0;
			//float horizontal=1;
			gameObject.GetComponent<Animation>().Blend ("X0_3", 1F, 2F);
			//gameObject.animation.Blend ("show_right", 1-horizontal, 2.0F);
			gameObject.GetComponent<Animation>().Blend ("X0_2",1F, 2F);
			//gameObject.animation.Blend ("s0_1", 1-vertical, 2F);
		}
		
		
	}
}