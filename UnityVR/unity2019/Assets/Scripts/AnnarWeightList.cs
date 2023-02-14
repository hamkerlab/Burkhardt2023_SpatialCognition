/**
@brief
  AnnarWeightList stores a list of AnnarWeight together with a type information of these weights

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using System;
using System.Collections.Generic;
using ProtoBuf;

[Serializable, ProtoContract]
public class AnnarWeightList
{
	/// <summary>
	/// Weight type
	/// </summary>
	[ProtoMember(1)]
	public int Type {get; set;}
	
	/// <summary>
	/// List of Weights
	/// </summary>
	[ProtoMember(2)]
	public List<AnnarWeight> Weights  {get; set;}

	/// <summary>
    /// This standard constructor is necessary for protobuf
	/// </summary>
	private AnnarWeightList ()
	{
	}
	
	/// <summary>
	/// Initializes a new instance of the <see cref="AnnarWeightList"/> class.
	/// </summary>
	/// <param name='type'>
	/// Type.
	/// </param>
	/// <param name='weights'>
	/// Weights.
	/// </param>
	public AnnarWeightList (int type, List<AnnarWeight> weights)
	{
		Type = type;
		Weights = weights;		
	}
	
	/// <summary>
	/// Gets the weight with specific ID.
	/// </summary>
	/// <returns>
	/// Weight with specific ID
	/// </returns>
	/// <param name='id'>
	/// ID.
	/// </param>
	public AnnarWeight getWeight (int id)
	{
		return Weights [id];
	}
	
	
	
}

