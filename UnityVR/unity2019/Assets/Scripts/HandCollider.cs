/**
@brief Handles collisions of the hand component

@details 
 - Mechanism in the case an object is useable
   - The tag "usable" denotes that the object can either be grasped, pointed or interacted.
   - The object itself has to be tagged with "useable"
   - agentHand and object needs both collider and rigidbodies
   - istrigger and isKenematic have to be off (see next case), so we use the OnCollisonEnter function
   - OnCollisionEnter recognize that the object should be used if: 
     1) the object is tagged with useable
     2) the hand is tagged with agentHand
     3) the action is executed dependet if an msgGrasp, msgPoint or msgInteraction is currently executed
   - For detailed procedure how to grasp, see the comments in the source code

 - Mechanism in the case an object is NOT useable
   - Object is not usable, if no tag "usable" is applied
   - Intended behavipour is that the hand pushes the object away
   - So agentHand and object needs both collider and rigidbodies
   - istrigger and isKenematic have to be off for both to use the physics calculation
   - Through physics, the object is pushed away
   - The hand would be also pushed away, to avoid this position and rotation have to be frozen
 
 - Settings for the hand of an agent:
   - to be taged as "hand"
   - collider with isTrigger=off
   - collider with freezed position and rotation
   - rigidbody with useGravity=off
   - This script
 - Settings for all graspable objects
   - to be taged as "agentHand"
   - collider
   - rigidbody
 
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using System.Collections;
using UnityEngine;

public class HandCollider : MonoBehaviour
{
    #region Fields

    /// <summary>
    /// GameObjID of object we collided with
    /// </summary>
    public int HitID;

    /// <summary>
    /// GameObjName of object we collided with
    /// </summary>
    public string HitName = string.Empty;

    /// <summary>
    /// GameObject we collided with
    /// </summary>
    public GameObject HitGameObject;
	
    /// <summary>
    /// Tag of object we collided with
    /// </summary>
    public string HitTag = string.Empty;
	
	/// <summary>
	/// The power to push an object away through collision.
	/// </summary>
    public float pushPower = 2.0F;

    #endregion Fields
	
	/// <summary>
	/// The associated agent. As this script is typically attached to a sub-object of an agent, the reference is stored seperatly.
	/// </summary>
	AgentScript agent = null;
		
	
	#region PrivateMethods	
	
	void Awake()
	{
		// search for agent parent object via loop		
		Transform parent = gameObject.transform.parent;
		while (parent != null) 
		{
			if (parent.tag == "agent") 
			{
				//assume only one script is active => search it
				AgentScript [] agents = parent.gameObject.GetComponents<AgentScript>();
				for(int i=0; i<agents.Length; i++)
				{
					if(agents[i].enabled)
					{
						agent = agents[i];
					}
				}
				break;
			}
			parent = parent.transform.parent;
		}
		if(agent == null)
			Debug.Log("Could not find parent agent object for object '" + gameObject +"'");
		else
			Debug.Log("Agent=" + agent);
		
		//avoid physical forces for collisions with the table. They must be tagged as "noHandPhysic" //<- disabled duo to freezing!
/*		GameObject [] xs = GameObject.FindGameObjectsWithTag("noHandPhysic");
        
        foreach (GameObject x in xs) 
		{
			Physics.IgnoreCollision(x.collider, this.collider);
        }*/
		
		// avoid physical forces for collisions with the agent themself
		// This is not really encessary due to freezed position7rotation of the hand, but should speed up physic calculation
		Physics.IgnoreCollision(agent.GetComponent<Collider>(), this.GetComponent<Collider>());
		
	}	
	
    /// <summary>
    /// CollisionEventHandler (OnTriggerEnter => touching objects event, OnCollisionEnter => touching objects plus physic calulation (needs 2 non-kineamatic rigidbodies to be called))
    /// </summary>
    void OnTriggerEnter(Collider hit) 
    {
		//Debug.Log("Collision event: object " + gameObject + " with="+hit); //DEBUG
		
		this.HitGameObject = null;
		// Security check
        if (hit == null)
			return;
		
	    if (hit.GetComponent<Rigidbody>() != null)
        {
			//hit an object containing an rigidbody
            this.HitGameObject=hit.attachedRigidbody.gameObject;			
			this.HitTag = HitGameObject.tag.ToString();
            this.HitName = HitGameObject.name.ToString();
            this.HitID = HitGameObject.GetInstanceID();            
		}
		
		//if rigidbody is 0, try parent object with rigid body. Sometimes, collider are on sub-components
		else
		{
			Transform parent = hit.gameObject.transform.parent;
			if(parent != null && parent.GetComponent<Rigidbody>() != null)
			{
				//hit an object containing an rigidbody
	            this.HitGameObject=parent.GetComponent<Rigidbody>().gameObject;			
				this.HitTag = HitGameObject.tag.ToString();
	            this.HitName = HitGameObject.name.ToString();
	            this.HitID = HitGameObject.GetInstanceID();        
			}
		}
		
		if(this.HitGameObject != null)
		{
			
			//Debug.Log("Detect collision with " + HitName + ": tag=" + HitTag); //DEBUG        
			
			if(this.HitTag == "usable" && gameObject.tag=="agentHand" && agent.getRightGraspedObject() == null)
			{			
			
				//grasp it by: 1) attach to parent, 2) stop movement and rotation 3) disable gravity 4) move (+rotate) it to the middle or otherwise correctly 5) disable physic to avoid forces from other collisions
				if(agent.getLastArmMsg() == AgentScript.ArmMsg.ArmMsgGrasp)
				{			
		
					//read position/rotation from the agent csv file for the hitted prefab
					Vector3 pos = new Vector3(0,0,0);
					Quaternion quat = new Quaternion(1,0,0,0);
					//is null if no specific position or quaternion are defined. In this case use standard values 
					if(agent.csvReaderAnim != null)
						agent.csvReaderAnim.SearchInformation(HitName, out pos, out quat);
							
					hit.attachedRigidbody.gameObject.transform.parent = gameObject.transform;
					hit.attachedRigidbody.velocity = Vector3.zero;
					hit.attachedRigidbody.angularVelocity = Vector3.zero;
					hit.attachedRigidbody.useGravity = false;
					hit.attachedRigidbody.gameObject.transform.localPosition = pos; 
					hit.attachedRigidbody.gameObject.transform.localRotation = quat; 
					hit.attachedRigidbody.isKinematic = true; //disable pyhsics
					
					agent.setRightGraspedObject(HitGameObject);
					
					Debug.Log("Grasp object '" + HitName + "' with '" + gameObject.name + "'"); //DEBUG
				}
			}
		}
    }
	
	/// <summary>
    /// CollisionEventHandler for hand.isTrigger==off. 
    /// I implement both version in the case the trigger-property is changed.
    /// </summary>
	void OnCollisionEnter(Collision col)
    {
		OnTriggerEnter(col.collider);
    }

    #endregion PrivateMethods
}