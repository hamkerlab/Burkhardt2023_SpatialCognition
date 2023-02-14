using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;
namespace SimpleNetwork
{

    /// <summary>
    /// A container class which can contain all types of messages. It can also contain a debug.
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgObject
    {
        public MsgObject() { }//Protobuff needs a Constructor without params
        

        //spaetere optimierung: nicht so abstrakt
        public MsgObject(Object Contend)
        {
            Type TypeOfContend = Contend.GetType();
            foreach (var Field in this.GetType().GetFields())
            {
                if (Field.FieldType == TypeOfContend)
                {
                    Field.SetValue(this, Contend);
                    return;
                }
            }
            throw new Exception("Could not save Contend in to MsgObject. Type of contend not known.");
        }

        [ProtoMember(1)]
        public MsgAgentMovement msgAgentMovement;

        [ProtoMember(2)]
        public MsgAgentEyemovement msgAgentEyemovement;

        [ProtoMember(3)]
        public MsgAgentEyeFixation msgAgentEyeFixation;
        
        [ProtoMember(4)]
        public MsgReward msgReward;

        [ProtoMember(5)]
        public MsgGridPosition msgGridPosition;

        [ProtoMember(6)]
        public MsgActionExecutionStatus msgActionExecutationStatus;

        [ProtoMember(7)]
        public MsgCollision msgCollision;

        [ProtoMember(8)]
        public MsgImages msgImages;

        [ProtoMember(9)]
        public MsgMenu msgMenu;

        [ProtoMember(10)]
        public string msgDebug;

        [ProtoMember(11)]
        public MsgEnvironmentReset msgEnvironmentReset; 

        [ProtoMember(12)]
        public MsgTrialReset msgTrialReset; 
        
        [ProtoMember(13)]
        public MsgAgentGraspPos msgAgentGraspPos; 
        
        [ProtoMember(14)]
        public MsgAgentGraspID msgAgentGraspID; 
        
        [ProtoMember(15)]
        public MsgAgentPointPos msgAgentPointPos;  
        
        [ProtoMember(16)]
        public MsgAgentPointID msgAgentPointID; 
        
        [ProtoMember(17)]
        public MsgAgentInteractionID msgAgentInteractionID; 
        
        [ProtoMember(18)]
        public MsgAgentInteractionPos msgAgentInteractionPos;

        [ProtoMember(19)]
        public AnnarNetwork msgAnnarNetwork;

        [ProtoMember(20)]
        public MsgStartSync msgStartSync;

        [ProtoMember(21)]
        public MsgStopSync msgStopSync;

        [ProtoMember(22)]
        public MsgAgentGraspRelease msgAgentGraspRelease;

        [ProtoMember(23)]
        public MsgAgentTurn msgAgentTurn;

        [ProtoMember(24)]
        public MsgEyePosition msgEyePosition;
		
		[ProtoMember(25)]
        public MsgObjectPosition msgObjectPosition;

        [ProtoMember(26)]
        public MsgHeadMotion msgHeadMotion;

        [ProtoMember(27)]
        public MsgAgentMoveTo msgAgentMoveTo;

        [ProtoMember(28)]
        public MsgAgentCancelMoveTo msgAgentCancelMoveTo; 

        [ProtoMember(29)]
        public MsgVersionCheck msgVersionCheck; 
		
		[ProtoMember(30)]
        public MsgSaccFlag msgSaccFlag; 
        
    }
}
