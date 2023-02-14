/**
@brief Control class for the environment in the "BrainVisio" scenario.

@details
 - The BrainVisio scenario visualize the second layer of the Neuronalfield
 
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

public class BrainVisioBehavior : BehaviourScript
{
    #region Fields

    #endregion Fields

	#region ProtectedMethods	
	
	/// <summary>
    /// Overridden function for creation of the agent gameObject in the scene: 
    ///   - It will set the Cathegory variables to empty lists
    ///   - It also create one agent
    /// </summary>
    protected override void AgentInitalization()
    {
		
		// find all agent OBJECTS  in the scene containing a specific script
		getAllAgentObjects<BrainVisioAgent>();
		
		// find and init all agent SCRIPTS  in the scene containing a specific script
		getAndInitAllAgentScripts<BrainVisioAgent>();

		//TODEL
		Debug.Log("Agents size: " + agents.Length);
		Debug.Log("script size: " + agentScripts.Length);
    }

	#endregion ProtectedMethods	
	
	#region PrivateMethods
    
	#endregion PrivateMethods
	
	#region InternalMethods	
	
    #endregion InternalMethods	
}
