/**
@brief
   AnnarLayer represents a single layer in a neuronal network.
   AnnarLayer contains a list of AnnarNeuron and provides access methods for these.
   
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using System;
using System.Collections.Generic;
using ProtoBuf;

[Serializable, ProtoContract]
public class AnnarLayer
{
	
	/// <summary>
	/// Width of the layer
	/// </summary>
	[ProtoMember(1, IsRequired = true)]
	public int Width {get;set;}
	
	/// <summary>
	/// Height of the layer
	/// </summary>
	[ProtoMember(2, IsRequired = true)]
	public int Height{get;set;}
	
	/// <summary>
	/// Depth of the layer
	/// </summary>	
	[ProtoMember(3, IsRequired = true)]
	public int Depth{get;set;}
	
	/// <summary>
	/// Name of the layer
	/// </summary>
	[ProtoMember(4, IsRequired = true)]
	public string Name{get;set;}
	
	/// <summary>
	/// ID of the layer
	/// </summary>
	[ProtoMember(5, IsRequired = true)]
	public int Id {get;set;}
	
	/// <summary>
	/// List of all neurons
	/// </summary>
	[ProtoMember(6)]
	public List<AnnarNeuron> Neurons {get;set;}
	
	/// <summary>
    /// This standard constructor is necessary for protobuf
	/// </summary>
	private AnnarLayer ()
	{
	}
	
	/// <summary>
	/// Initializes a new instance of the <see cref="AnnarLayer"/> class.
	/// </summary>
	/// <param name='width'>
	/// Width.
	/// </param>
	/// <param name='height'>
	/// Height.
	/// </param>
	/// <param name='depth'>
	/// Depth.
	/// </param>
	/// <param name='name'>
	/// Name.
	/// </param>
	/// <param name='id'>
	/// Identifier.
	/// </param>
	/// <param name='neurons'>
	/// Neurons.
	/// </param>
	public AnnarLayer (int width, int height, int depth, string name, int id, List<AnnarNeuron> neurons)
	{
		Width = width;
		Height = height;
		Depth = depth;
		Name = name;
		Id = id;
		Neurons = neurons;
	}
	
	/// <summary>
	/// Get a neuron.
	/// </summary>
	/// <returns>
	/// The neuron at specific position.
	/// </returns>
	/// <param name='pos'>
	/// Position of the neuron.
	/// </param>
	public AnnarNeuron getNeuron (int id)
	{
		return Neurons [id];
	}

    /// <summary>
    ///  Get a neuron.
    /// </summary>
    /// <returns>
    /// The neuron at specific position.
    /// </returns>
    /// <param name='width'>
    /// Width.
    /// </param>
    /// <param name='height'>
    /// Height.
    /// </param>
    /// <param name='depth'>
    /// Depth.
    /// </param>
    public AnnarNeuron getNeuron(int w, int h, int d = 0)
    {
        return Neurons[getNeuronRank(w, h, d)];
    }

    /// <summary>
    /// Returns rank of neuron with coordinates w,h,d
    /// </summary>
    /// Neurons are ordered: 1) depth, 2) widht, 3) height (like an RGB image)
    /// Should be changed for ANNarchy 3.x!
    public int getNeuronRank(int w, int h, int d)
    {
        // Manage indexing error
        // TODO: add output to logfile
        if (w < 0 || w >= Width)
        {
            string str = "Neuron doesn't exist! : [w/h/d]=[" + w + "/" + h + "/" + d + "] - expected 0<=w<" + Width + "! -";
            //Debug.Log(str);
            return 0;
        }
        if (h < 0 || h >= Height)
        {
            string str = "Neuron doesn't exist! : [w/h/d]=[" + w + "/" + h + "/" + d + "] - expected 0<=h<" + Height + "! -";
            //Debug.Log(str);
            return 0;

        }
        if (d < 0 || d >= Depth)
        {
            string str = "Neuron doesn't exist! : [w/h/d]=[" + w + "/" + h + "/" + d + "] - expected 0<=d<" + Depth + "! -";
            //Debug.Log(str);
            return 0;
        }

        return d + Depth * w + Depth * Width * h;
    }   
	
	/// <summary>
	/// Returns a <see cref="System.String"/> for printing the current <see cref="AnnarLayer"/>.
	/// </summary>
	/// <returns>
	/// A <see cref="System.String"/> for printing the current <see cref="AnnarLayer"/>.
	/// </returns>
	public override string ToString ()
	{
		return "AnnarLayer:" + System.Environment.NewLine +
			    "\tname = " + Name + System.Environment.NewLine +
				"\twidth = " + Convert.ToString (Width) + System.Environment.NewLine +
				"\theight = " + Convert.ToString (Height) + System.Environment.NewLine +
				"\tdepth = " + Convert.ToString (Depth) + System.Environment.NewLine +
				"\tNumOfNeurons = " + Convert.ToString (Neurons.Count);
	}
		
}
