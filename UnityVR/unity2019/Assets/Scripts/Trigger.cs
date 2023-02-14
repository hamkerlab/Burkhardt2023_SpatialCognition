/**
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using UnityEngine;
using System.Collections;

public class Trigger : MonoBehaviour {
	// Reward for the object
	public int id;

	// If Lerpz enters the Trigger a reward (id) gets sent
	void OnTriggerEnter(Collider other) {
		if (other.gameObject.name=="Lerpz"){

			other.GetComponent<MyLearningroomAgentScript>().ReceiveReward((float)id);
			if(id == 0 || id == 2){
				other.GetComponent<MyLearningroomAgentScript>().StartNewMovement(1f,360.0f);
			}
			
		}
	}
}
