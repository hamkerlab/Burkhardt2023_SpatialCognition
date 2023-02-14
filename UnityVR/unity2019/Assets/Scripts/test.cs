/**
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using UnityEngine;
using System.Collections;

public class test : MonoBehaviour {

	// Use this for initialization
	void Start () {
	
	}
	
	// Update is called once per frame
	void Update () {
	if (Input.GetKey (KeyCode.A)) {
	transform.Translate(new Vector3(-1f*Time.deltaTime,0,0)); }
	if (Input.GetKey (KeyCode.D)) {
	transform.Translate(new Vector3(1f*Time.deltaTime,0,0));
	}
	if (Input.GetKey (KeyCode.W)) {
	transform.Translate(new Vector3(0,0,1f*Time.deltaTime));
	
	}
	if (Input.GetKey (KeyCode.S)) {
	transform.Translate(new Vector3(0,0,-1f*Time.deltaTime));
	}
	if (Input.GetKeyUp (KeyCode.Space)) {
	transform.Translate(new Vector3(0,3,0)); }
	}
}
