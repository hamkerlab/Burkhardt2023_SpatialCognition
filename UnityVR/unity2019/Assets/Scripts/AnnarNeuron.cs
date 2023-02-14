/**
@brief  
  AnnarNeuron represents a single neuron which can have a number of connections to other neurons.
  These connections are stored in WeightLists
 
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using System;
using System.Text;
using System.Collections.Generic;
using ProtoBuf;

[Serializable, ProtoContract] 
public class AnnarNeuron
{
	/// <summary>
	/// Membran potential
	/// </summary>
	[ProtoMember(1)]
	public double Mp {get; set;}
	
	/// <summary>
	/// Firing rate
	/// </summary>
	[ProtoMember(2)]
	public double Rate  {get; set;}

    /// <summary>
    /// ID
    /// </summary>
    [ProtoMember(3)]
    public int Id { get; set; }	

	/// <summary>
	/// List of AnnarWeightLists attached to this neuron
	/// </summary>
	[ProtoMember(4)]
	public List<AnnarWeightList> WeightLists  {get; set;}
	
    /// <summary>
    /// This standard constructor is necessary for protobuf
    /// </summary>
	private AnnarNeuron ()
	{
	}
	
	
	/// <summary>
	/// Initializes a new instance of the <see cref="AnnarNeuron"/> class.
	/// </summary>
	/// <param name='mp'>
	/// Membran potential
	/// </param>
	/// <param name='rate'>
	/// Firerate
	/// </param>
	/// <param name='weightLists'>
	/// Weight lists.
	/// </param>
	public AnnarNeuron (double mp, double rate, List<AnnarWeightList> weightLists)
	{
		Mp = mp;
		Rate = rate;
		WeightLists = weightLists;
	
	}
	
	
	/// <summary>
	/// Iterator for Weights of specific type
	/// </summary>
	/// <returns>
	/// Iterator for Weights of specific type
	/// </returns>
	/// <param name='type'>
	/// Type.
	/// </param>
	public IEnumerable<AnnarWeight> getTypedWeights (int type)
	{
		foreach (var weightList in WeightLists) {
			if (weightList.Type == type) {
				foreach (var weight in weightList.Weights) {
					yield return weight;
				}
			}
		}
	}
	
	
	/// <summary>
	/// Iterator for Weights with a specific ID in <see cref="WeightLists"/>
	/// </summary>
	/// <returns>
	/// Iterator for Weights with a specific ID
	/// </returns>
	/// <param name='id'>
	/// Identifier.
	/// </param>
	public IEnumerable<AnnarWeight> getWeights (int id)
	{		
			
		foreach (var weight in WeightLists[id].Weights) {
			yield return weight;
		}
			
	}
	
	
	
	/// <summary>
	/// Returns a <see cref="System.String"/> that represents the current <see cref="AnnarNeuron"/>.
	/// </summary>
	/// <returns>
	/// A <see cref="System.String"/> that represents the current <see cref="AnnarNeuron"/>.
	/// </returns>
	public override string ToString ()
	{
		
		StringBuilder sb = new StringBuilder ();
		
		sb.AppendLine (
			string.Format ("[AnnarNeuron: Mp={0}, Rate={1}]", 
				Mp, 
				Rate)
			);
		
		if(WeightLists != null)
		foreach (var weightList in WeightLists) {
			foreach (var weight in weightList.Weights) {
				sb.AppendLine (
						string.Format ("[AnnarWeight: Type={0}, PreNeuronID={1}, PreLayerID={2}, WeightValue={3}]", 
										weightList.Type,
										weight.PreNeuronID,
										weight.PreLayerID,
										weight.WeightValue)
					);
			}
		}
		
		return sb.ToString ();	
	}

}
