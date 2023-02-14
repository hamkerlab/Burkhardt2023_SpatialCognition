/**
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using System;
using System.Collections;
using SimpleNetwork;
using UnityEngine;

public class MyLearningroomAgentScript : AgentScript {

	// Amount already rotated of current rotation
	float totalRotation = 0;

	// Current target rotation
	float targetRotation;

	// Current target position
	Vector3 targetPosition;

	// Is a search currently active
	bool search = true;

	// Controls execution of search
	int searchStep = 0;

	// Handles rotation and movement during search
	public void handleSearch(int step){
		// Rotation
		if (step == 1) {
			float currentAngle = transform.rotation.eulerAngles.y;
		    transform.rotation = Quaternion.AngleAxis (currentAngle + (Time.deltaTime * targetRotation), Vector3.up);
			totalRotation += Time.deltaTime * Mathf.Abs(targetRotation);
		}
		// Movement
		else if(step==2){
			Vector3 direction = targetPosition - transform.position;
			direction.y = 0;
			Vector3 v= Vector3.ClampMagnitude(direction * 2f, 2f);
			if(v.magnitude <= 0.1)
				searchStep = 0;		
			GetComponent<CharacterController>().SimpleMove(v);
		}
	
	}

	// If Lerpz collides with an object he turns around and contiues the search
	void OnControllerColliderHit(ControllerColliderHit hit){
		if (hit.gameObject.name != "Terrain") {
						targetRotation = 180f;
						searchStep = 1;
				}
	}
}
	