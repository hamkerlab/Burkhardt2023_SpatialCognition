/**
@brief Class for an BrainVisio agent. It demonstrate the visualisation of a neuronal network (ANNarchy)
@details
 - Created on: February 2013 
 - The BrainVisio scenario visualize the second layer of the Neuronalfield
 
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using System;
using System.Collections;
using SimpleNetwork;
using UnityEngine;

public class BrainVisioAgent : AgentScript
{
    #region PublicMethods

	private GameObject rendercube;  // the cube to visualize the firing rates
	private AnnarNetwork MyAnnarNetwork; //attached ANNarchy network
	private Texture2D texture;      // the texture on the cube
	
	private bool verbose = false; // if true, print an info forreceiving of every message

    #endregion PublicMethods


    #region ProtectedMethods
	void Start()
	{
		MyAnnarNetwork = null;
		
		rendercube = Instantiate(Resources.Load("RenderCubePrefab") as UnityEngine.Object, new Vector3(2f,3f,1f), Quaternion.identity) as GameObject;
	}
			

    /// <summary>
    /// when recieving MsgAnnarNetwork with Update = false
    /// </summary>
    /// <param name="msg">MsgAnnarNetwork object</param>    
    protected override void ProcessMsgAnnarNetwork(AnnarNetwork msg)
    {
		if(MyAnnarNetwork == null)
		{
			MyAnnarNetwork = msg;
			texture = new Texture2D(MyAnnarNetwork.getLayer(1).Width, MyAnnarNetwork.getLayer(1).Height);
	        rendercube.GetComponent<Renderer>().material.mainTexture = texture;			
		}
		
        Debug.Log(String.Format("AnnarNetwork structure received\n"));
		
		if(verbose) {
			for(int l=0; l < msg.Layers.Count; l++)
			{
				Debug.Log(String.Format(msg.Layers[l].ToString()));
			}
			Debug.Log(String.Format(
				
					"Receive Netork structure at t=" + msg.step + "\n" + 
				    "PARENT LAYER: " + msg.Layers[0].Name + " | " + msg.Layers[1].Name + "\n" +
					"MP: \t\t\t\t\t\t " + msg.Layers[0].Neurons[0].Mp + " | " + msg.Layers[1].Neurons[0].Mp + "\n" +
					"RATE: \t\t\t\t\t " + msg.Layers[0].Neurons[0].Rate + " | " + msg.Layers[1].Neurons[0].Rate + "\n"));
		}
    
	}

    /// <summary>
    /// when recieving MsgAnnarNetwork with Update = true
    /// </summary>
    /// <param name="msg">MsgAnnarNetwork object</param>    
    protected override void ProcessMsgAnnarUpdateRates(AnnarNetwork msg)
    {		
		if(verbose) {
			Debug.Log(String.Format(
				
					"UPDATE Neuron at t=" + msg.step + "\n" +
				    "PARENT LAYER: " + msg.Layers[0].Name + " | " + msg.Layers[1].Name + "\n" +
					"MP: \t\t\t\t\t\t " + msg.Layers[0].Neurons[0].Mp + " | " + msg.Layers[1].Neurons[0].Mp + "\n" +
					"RATE: \t\t\t\t\t " + msg.Layers[0].Neurons[0].Rate + " | " + msg.Layers[1].Neurons[0].Rate + "\n"));
		}
    
    	RenderCube(msg);
		
	}
	
	/// <summary>
	/// Renders firing rates of layer 1 of a neuronal network on a cube.
	/// </summary>
    /// <param name="msg">MsgAnnarNetwork object</param>  
    void RenderCube (AnnarNetwork msg) 
	{
		if(MyAnnarNetwork != null)
		{
			// we only need the position [x,y] of a Neuron, so implementing the getNeuron an acompaning functions in AnnarLayer.cs analog to AnnarLayer.cpp would be redundant.
			// so all we have to do is to convert the ListIndex of those Neurons to a n-dimensional-arry-index wich in this case is 2.
			// Neurons[x,y] = Neurons[x*dimx + y], where dimx is the dimension of the first Index (i.e. texture.width == 32).
			// Update: 6.6.2013: AnnarLayer has now an 2D and 3D index and getneuron function => use them as A) the index calculation will change in further ANNarchy version and B) the above calculation is maybe wrong for depth>0
					
			
			int y = 0;
	        while (y < texture.height) {
	            int x = 0;
	            while (x < texture.width) 
				{
					//float rate = (float)msg.Layers[1].Neurons[x*texture.width+y].Rate;
					float rate = (float)msg.getLayer(1).getNeuron(x,y).Rate;		
					if(rate>1.0)
						rate = 1.0f;
					Color color = new Color(rate, rate, rate);				
	                texture.SetPixel(x, y, color);
	                ++x;
	            }
	            ++y;
	        }
			
			texture.Apply();
		}
		else
		{
			Debug.Log("ANNarchy network structure was not received, wait for it..\n");
		}
	}
	 
    #endregion ProtectedMethods
}
