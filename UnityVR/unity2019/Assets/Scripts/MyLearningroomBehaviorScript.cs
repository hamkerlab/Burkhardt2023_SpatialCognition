/**
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using SimpleNetwork;

using UnityEngine;


public class MyLearningroomBehaviorScript : BehaviourScript {

	// Spawn point enumeration
	public enum level 
	{
		spawn1 = 1,
		spawn2 = 2
	};

	// Selected spawn point
	public level select = level.spawn1;


	GameObject agent;

	// Initalization
	protected override void AgentInitalization()
	{		
		// find all agent OBJECTS  in the scene containing a specific script
		getAllAgentObjects<MyLearningroomAgentScript>();
		
		// find and init all agent SCRIPTS  in the scene containing a specific script
		getAndInitAllAgentScripts<MyLearningroomAgentScript>();

		// set default position to selected spawn point
		switch((int)select){
			case 1:
				agentScripts[0].DefaultAgentPosition = new Vector3(2.07f,0.25f,-6.35f); 
				break;
			case 2:
				agentScripts[0].DefaultAgentPosition = new Vector3(0.3f,0.25f,-8.5975f);
				break;
		}

		agentScripts[0].DefaultRotation = 0;

		Reset();
		
	}

	// Reset environment
	protected override void ProcessMsgEnvironmentReset( MsgEnvironmentReset msg )
	{			
 		
		Reset();
	}
	
}
