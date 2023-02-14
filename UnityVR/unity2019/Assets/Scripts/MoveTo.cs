/**
Controls the agent movement in the NavMesh

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/

    
using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System;
using System.Linq;
using SimpleNetwork;

public class MoveTo : AgentScript
{   		
	public Vector3 felice_position;
	public Vector3 destination;
	UnityEngine.AI.NavMeshAgent agent;
	
	
	protected override void ProcessMsgAgentMoveTo(MsgAgentMoveTo msg)
	{	
		
		if (MySimpleNet != null) 
		{
			MySimpleNet.Send (new SimpleNetwork.MsgActionExecutionStatus () {actionID = this.MovementIDExecuting, status = SimpleNetwork.MsgActionExecutionStatus.InExecution});
		}
		
		//mibur: NavMesh pathplanning
		Debug.Log ("Moving to item attached to script");
		Debug.Log("ID = ");
		Debug.Log(this.MovementIDExecuting);
		
		agent = GetComponent<UnityEngine.AI.NavMeshAgent>();
		agent.destination = destination;			
	}
	
	public void Update()
	{
		Debug.Log("Current Agent position:");
		Debug.Log(agent.transform.position);
	}
}
	
