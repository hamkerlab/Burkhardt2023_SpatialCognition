/**
@mainpage "Simulating of cognitive agent with active environment interaction in a virtual reality"
  This document describes all classes and structures of the virtual reality application, the main-class is BehaviourScript .

 @section General idea
 The BehaviourScript controls the whole VR. It assigns networkinterfaces to the agents, and has
 a networkinterface to receive commands concerning the running experiment. The AgentScript controls the
 agent figure. It sends images with its networkinterface and receives commands from the agent.

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

/** @brief
 * This class controls the whole VR. 
 *
 * It assigns Networkinterfaces to the Agents, and has a own networkinterface to receive commands that concern the running trail.
 * It's not indented that this class is directly attached to a 3D Object in Unity.
 * Therefore the user must create a derivided class for his scenario,
 * where the behavior to protobuf messages can be overridden.
 *
 * @details Responsibility of this class
 * - Network object creation
 * - Spawns agents
 * - Create and delete barriers
 * - GUI/Button handling (BehaviourScript::OnGUI)
 * - Actions
 * - Save camera images to disk for Debug purposes (BehaviourScript::SaveScreenPNG)
 *
 */
public partial class BehaviourScript : MonoBehaviour
{
    #region Fields

    /// <summary>
    /// Access to the agent GameObjects in scene
    /// </summary>
    protected GameObject[] agents;

    /// <summary>
    /// Access to the script controling the Agent
    /// </summary>
    protected AgentScript[] agentScripts;

    /// <summary>
    /// We make copys of this GameObject (a PreFab), if we want to add new Barriers (GUI function...) 
    /// </summary>
    protected GameObject Barrier;

    /// <summary>
    /// Global configuration object
    /// </summary>
    protected cConfiguration config;

    /// <summary>
    /// Networkinterface used by the VR
    /// </summary>
    protected SimpleNet MySimpleNet;

    /// <summary>
    /// name of the global configuration file.
    /// </summary>
    public string ConfigFileName = "APPConfig.config";

    #endregion Fields

	#region PublicMethods	
	

    /// <summary>
    /// Fired when VR shuts down
    /// </summary>
    public void OnApplicationQuit()
    {
        //shut down the networkinterface gracefully
        if (MySimpleNet != null)
        {
            Debug.Log("Stopping network...");
            MySimpleNet.Stop();
        }
		
		
    }
	 #endregion PublicMethodss
	
	
	
	
	
	 #region ProtectedMethods
    /// <summary>
    /// Creation of the Agent GameObjects in the scene (should be overridden in a derivided class)
    /// </summary>
    protected virtual void AgentInitalization()
    {
    }

    /// <summary
	/// For spherical projection
	/// </summary>
	protected virtual void cloneAgent()
	{
	}
	
	/// <summary>
    /// Behavior function for MsgEnvironmentReset (should be overridden in a derivided class)
    /// </summary>
    /// <param name="msg">MsgEnvironmentReset object</param>
    protected virtual void ProcessMsgEnvironmentReset( MsgEnvironmentReset msg )
    {	
		Reset();
    }

    /// <summary>
    /// Behavior function for MsgTrialReset (should be overridden in a derivided class)
    /// </summary>
    /// <param name="msg">MsgTrialReset object</param>
    protected virtual void ProcessMsgTrialReset( MsgTrialReset msg )
    {
        Reset();
    }

    /// <summary>
    /// Remove all Barrierobjects - Used by the VR- menu and resetfuntion
    /// </summary>
    protected void RemoveAllBarriers()
    {
        //delete everything with the tag "Barrier"
        GameObject[] Barriers = GameObject.FindGameObjectsWithTag("Barrier");
        foreach (GameObject obj in Barriers)
            Destroy(obj);
    }

    /// <summary>
    /// Resets the VR, you have to define your scenarios here!
    /// </summary>
    protected void Reset()
    {
		
		for(int i = 0; i < agentScripts.Length; i++)
		{
			agentScripts[i].AgentReset();
		}
		
        
        RemoveAllBarriers();

        //Want to create some objects on the Fly? learn how:
        //http://unity3d.com/support/documentation/Manual/Instantiating%20Prefabs.html
    }

    /// <summary>
    /// Make a Screenshot of VR-view
    /// </summary>
    /// <returns></returns>
    protected IEnumerator SaveScreenPNG()
    {
        Debug.Log("----SavePNG() called------");

        // We should only read the screen bufferafter rendering is complete
        yield return new WaitForEndOfFrame();
        //yield return 0;

        // Create a texture the size of the screen, RGB24 format
        int width = Screen.width;
        int height = Screen.height;
        Texture2D tex = new Texture2D(width, height, TextureFormat.RGB24, false);

        // Read screen contents into the texture
        tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
        tex.Apply();

        // Encode texture into PNG
        byte[] bytes = tex.EncodeToPNG();
        Destroy(tex);

        Debug.Log("---SavedScreen.png--- unter : " + Application.dataPath.ToString() + " with " + bytes.Length.ToString());

        // For testing purposes, also write to a file in the project folder
        try
        {
            File.WriteAllBytes(Application.dataPath + "/../SavedScreen.png", bytes);
        }
        catch (Exception exe)
        {
            Debug.Log(exe.ToString());
        }
    }
	#endregion ProtectedMethods	
	
    #region InternalMethods	
	
	/// <summary>
	/// Search for all agent objects in the scene, recognizable by tag "agent".
	/// Have to search only for a specific type T of agentScripts as one object could contain several scripts.
	/// </summary> 
	protected void getAllAgentObjects<T>() where T : AgentScript
	{		        
		GameObject[] unsortedAgents = GameObject.FindGameObjectsWithTag("agent");
				
		//BubbleSort: sort list after AgentID
		GameObject tmpObj;		
		for (int n=unsortedAgents.Length; n>1; n--){
    		for (int i=0; i<n-1; i++){
				GameObject A1 = unsortedAgents[i];
				GameObject A2 = unsortedAgents[i+1];
      			if (A1.GetComponent<T>().AgentID > A2.GetComponent<T>().AgentID){
        	    	tmpObj = unsortedAgents[i];
					unsortedAgents[i] = unsortedAgents[i+1];
					unsortedAgents[i+1] = tmpObj;
      			} 
			} 
  		} 
		agents = unsortedAgents;
		
	}
	
	/// <summary>
	/// Search for all agentScripts of type T, store them in "agentScripts" and init them.
	/// The search is based on the agent stored in list "agents", see call getAllAgentObjects() before this function
	/// Have to use a specific type as one object could contain several scripts.
	/// </summary>
	protected void getAndInitAllAgentScripts<T>() where T : AgentScript
	{
		agentScripts = new AgentScript[agents.Length];
		Debug.Log("Init "+agents.Length+" agents...\n");
		
		for(int i = 0; i < agents.Length; i++)
		{
			agentScripts[i] = agents[i].GetComponent<T>();
			T curAgentScript = (T)agentScripts[i];
			string localIP = config.IPAddress;
            curAgentScript.InitializeFromConfiguration( config, localIP, agentScripts[i].AgentID );		
        	//Do NOT call agentScripts [i].AgentReset (), here this should be done at runtime (see AgentScript::update() )
		}
	}
	
	/// <summary>
    /// Get local IP
    /// </summary>
	protected string GetLocalIP()
	{
		if (!System.Net.NetworkInformation.NetworkInterface.GetIsNetworkAvailable())
    	{
        	return null;
    	}
        IPAddress i = Dns.GetHostAddresses(Dns.GetHostName())[config.IPAddressEntry];
        return i.ToString();
	}
	

    /// <summary>
    /// Unity doesnt allow conventional constructors, but provides this function for initialisations
    /// </summary>
    protected virtual void Awake()
    {
		
		if(this.enabled)
		{
		
	        //load configfile
	        config = new cConfiguration(ConfigFileName);
			string localIP = config.IPAddress;
			
	        Debug.Log("Local IP: " + localIP);
	        Debug.Log("Local environment port: " + config.LocalPort);
			Debug.Log("SyncMode: " + config.SyncMode);
	
            try
            {
                // TODO: retrieve from config???
                MySimpleNet = new SimpleNet(localIP, config.LocalPort);

            }catch(Exception e){
                Debug.Log(e.Message);
            }
			cloneAgent();
			
	        AgentInitalization();
	        // Make the game run even when in background
	        Application.runInBackground = true;
	
	        //Simulationspeedup
	        //>1 faster
	        //<1 slower
	        Time.timeScale = 1;
		}
    }

    /// <summary>
    /// Update is called once per frame and handles the VR-logic and messaging
    /// For agent related sensor events and actions, see AgentScript 
    /// </summary>
    protected virtual void Update()
    {
        #region handle incoming msg
		if(MySimpleNet != null)

        if (MySimpleNet.MsgAvailable())
        {
            MsgObject NextMsg = MySimpleNet.Receive();

            //Enviroment reset in the Moment only one configuration
            //MsgEnvironmentResetCodePosition
            if(NextMsg.msgEnvironmentReset != null)
                ProcessMsgEnvironmentReset( NextMsg.msgEnvironmentReset );

            //MsgTrailResetCodePosition
            //do what ever you want ;D
            //for testing, same as EnviromentReset
            if(NextMsg.msgTrialReset != null)
                ProcessMsgTrialReset( NextMsg.msgTrialReset );

        }
        #endregion
    }

    #endregion InternalMethods
}
