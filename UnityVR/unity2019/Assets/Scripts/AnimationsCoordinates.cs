/**
@brief Test for animations
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using UnityEngine;
using System.Collections;
using System;


public class AnimationsCoordinates : MonoBehaviour {

	// Use this for initialization
	void Start () {
	}
	
	// Update is called once per frame
	void Update () {
		
		float x,y,z;
		GameObject Hand=GameObject.Find ("rHand");
		x= Hand.transform.position.x;
		y= Hand.transform.position.y;
		z= Hand.transform.position.z;
		
		//string table = x.ToString()+ ";" + y.ToString()+";"+z.ToString()+ Environment.NewLine;
		
		//string table=String.Format("{0},{1},{2},",x,y,z);
			
//		Logger.Instance.Log(table);
	}

	void OnApplicationQuit() {
		
//		Logger.SaveToFile(@"C:\Users\jeoe\desktop\Coordinates.txt");
	}
}
