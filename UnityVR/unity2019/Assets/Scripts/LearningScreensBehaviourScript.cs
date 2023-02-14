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


public class LearningScreensBehaviourScript : BehaviourScript {

    GameObject[] spawns = null;

			public int table1;
			public int table2;
			public int table3;
			public int obj1;
			public int obj2;
		
				
			public int obj3;
			
			public string objectname1 = "", objectname2 = "", objectname3 = "";
			
			public int rot1;
			public int rot2;
			public int rot3;
			
			public double rotat1;
			public double rotat2;
			public double rotat3;
			
			public double degtorad1;
			public double degtorad2;
			public double degtorad3;

			public float rotx1, rotx2, rotx3;
			public float roty1, roty2, roty3;
			public float rotz1, rotz2, rotz3;

			public float agentpos_test;
	
			public int agentposrandom;
			public int agentposrandomcsv;
			

			public float penx1, penz1;
			public float penx2, penz2;
			public float penx3, penz3;
			
			
			public float objx1;
			public float objy1;
			public float objz1;
			
			public float objx2;
			public float objy2;
			public float objz2;
		
			public float objx3;
			public float objy3;
			public float objz3;
			
			
			public float boxx;
			public float boxy;
			public float boxz;
			
			
			public int rewardobject1 = 0;
			public int rewardobject2 = 0;
			public int rewardobject3 = 0;
			
			public int finalreward = 0;
			
			
			
			public float rotation;
            public int distance;
            public int object_id;
            public int MsgCpy;

			
			public int testagent = 1, testtable = 1;
			
			

			
			
			
    #region ProtectedMethods

    protected override void AgentInitalization() {
    

        getAllAgentObjects<TestObjectAgentScript>();


        getAndInitAllAgentScripts<TestObjectAgentScript>();

		// AGENT POSITION
		agentScripts[0].DefaultAgentPosition = new Vector3(2.066f, 0.2485f, -7.06f - (0.75f * distance));
		agentScripts[0].DefaultRotation = 0;

		Reset();



    }




    protected override void ProcessMsgTrialReset(MsgTrialReset msg) {
		


		
		// 72 rotations
		// 3 distances
		// 7 objects

		// -> 4135 -> 4th object, 1st distance, 35th rotation


		MsgCpy = msg.Type;
		//float agentpos_msg = (float)(msg.Type / 1000) / 10.0f;
		distance = MsgCpy / 1000;
		MsgCpy -= distance * 1000;

		object_id = MsgCpy / 100;
		MsgCpy -= object_id * 100;

		rotation = (MsgCpy * 5.0f)%360;


		// AGENT POSITION AND FUNCTION CALL TO SPAWN AND ROTATE OBJECT
		agentScripts[0].DefaultAgentPosition = new Vector3(2.066f, 0.2485f, -7.06f - (1f * distance));
		agentScripts[0].DefaultRotation = 0;

		Reset();

		learningScreensTable(msg.Type);	
    }

	
	protected void learningScreensTable(int msgcase) {


	
		// in the middle of the table
	
		float objx = 2.263f;
		float objy = 1.9165f;
		float objz = -5.1f;
	
		string objectname = "";

		float rotx = 0.0f;
		float roty = 0.0f;
		float rotz = 0.0f;
		


		switch(object_id){
			case 0:
				objectname = "car_crane_green";
				rotx = 270.0f;
				roty = 90.0f;
				break;
			case 1:
				objectname = "car_crane_yellow";
				rotx = 270.0f;
				roty = 90.0f;
				break;
			case 2:
				objectname = "dog";
				rotx = 270.0f;
				break;
			case 3:
				objectname = "racecar_blue";
				rotx = 270.0f;
				roty = 180.0f;
				break;
			case 4:
				objectname = "racecar_green";
				rotx = 270.0f;
				roty = 180.0f;
				break;
			case 5:
				objectname = "open_top_machine";
				rotx = 270.0f;
				roty = 130.0f;
				break;
			case 6:
				objectname = "teddy";
				rotx = 270.0f;
				roty = 180.0f;
				break;
		}

		if (spawns == null)
        {
            spawns = new GameObject[1];
        }
        else
        {
            for (int i = 0; i < 1; i++)
                UnityEngine.Object.Destroy(spawns[i]);
        }
        

        //automatic rotation


        /*if (msgcase >= 101+60 && msgcase <= 112+84) {
            double degtorad = rotat * Math.PI/180;
            objz = objz - (float)(Math.Cos(degtorad)*0.35);
            objx = objx - (float)(Math.Sin(degtorad)*0.35);
        }*/
			
			
			
			
			spawns[0] = (GameObject)Instantiate(GameObject.Find(objectname), new Vector3(objx, objy, objz), Quaternion.Euler(rotx, roty + rotation, rotz));
			spawns[0].tag = "usable"; spawns[0].name = "TestObject";            
    
	}


    #endregion ProtectedMethods
    
}





