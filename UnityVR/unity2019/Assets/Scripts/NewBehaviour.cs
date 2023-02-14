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

public class NewBehaviour : BehaviourScript
{	


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
			
    /// <summary>
    /// Overridden function for creation of the agent gameObject in the scene
    /// </summary>
    protected override void AgentInitalization()
    {
		// Find all agent OBJECTS  in the scene containing a specific script
		getAllAgentObjects<MoveTo>();
		
		// Find and init all agent SCRIPTS  in the scene containing a specific script
		getAndInitAllAgentScripts<MoveTo>();
		
		//Initialize Felice position
		agentScripts[0].DefaultAgentPosition = new Vector3(10.0f,0.02f,3.0f);
		agentScripts[0].DefaultRotation = 180;
    }
	

	
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////	
	
	/// <summary>
	/// Starts setup.
	/// </summary>
	/// <param name="msg">protobuf message</param>
	protected override void ProcessMsgEnvironmentReset( MsgEnvironmentReset msg )
    {			
		switch(msg.Type)
		{
		case 3:
			//agentScripts gets assigned in BehaviourScript l.283 
			agentScripts[0].DefaultAgentPosition = new Vector3(7.7f,0.02f,17.5f); 
			agentScripts[0].DefaultRotation = 180;
			GameObject.Find("MainCamera").transform.position = new Vector3(5.07f,11.26f,6.38f); 
			GameObject.Find("MainCamera").transform.eulerAngles = new Vector3(52.0f,69.3f,358.5f);
			break;
		
		default:
			agentScripts[0].DefaultAgentPosition = new Vector3(10f,0.02f,3f);
			break;
		}		
		
		Reset();
    }
}