/**
@brief  
  AnnarWeight represents a single connection between two neurons.
 
  Each AnnarNeuron contains 0 to n lists of AnnarWeightList 
  (which contains lists of AnnarWeight together with type information).
 
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using System;
using ProtoBuf;


[Serializable, ProtoContract] 
public class AnnarWeight
{		
	/// <summary>
	/// Connected with neuron with this ID
	/// </summary>
	[ProtoMember(1)]
	public int PreNeuronID {get; set;}
	
	/// <summary>
	/// Connected with a neuron in this layer
	/// </summary>
	[ProtoMember(2)]
	public int PreLayerID {get; set;}
	
	/// <summary>
	/// Weight value.
	/// </summary>
	[ProtoMember(3)]
	public double WeightValue {get; set;}
	
    /// <summary>
    /// This standard constructor is necessary for protobuf
    /// </summary>
	private AnnarWeight ()
	{
	}
	
	/// <summary>
	/// Initializes a new instance of the <see cref="AnnarWeight"/> class.
	/// </summary>
	/// <param name='preNeuronID'>
	/// Connecting to neuron with this ID
	/// </param>
	/// <param name='preLayerID'>
	/// Connecting with a neuron in this layer
	/// </param>
	/// <param name='weightValue'>
	/// Weight value.
	/// </param>
	public AnnarWeight (int preNeuronID, int preLayerID, double weightValue)
	{
		PreNeuronID = preNeuronID;
		PreLayerID = preLayerID;
		WeightValue = weightValue;
	}
	
}

