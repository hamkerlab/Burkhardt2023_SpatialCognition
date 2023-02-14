/**
@brief A class for reading CSV files

@detail CSVReder loads the CSV file as and list of string[] into the memory. 
        The SearchInformation function searches the data for a line, which contains 
		the position and rotation information of a referenced prefab.
 
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System;
using System.Globalization;
using System.Linq;

public class CSVReader
{
    private List<string[]> content;	
	
	/// <summary>
	/// Initializes a new instance of the <see cref="CSVReader"/> class and load the contant of the CSV file into the memory.
	/// </summary>
	/// <param name='Filename'>
	/// CSV filename
	/// </param>
	/// <param name='splitCharacter'>
	/// The character which splits the columns of the csv file
	/// </param>
    public CSVReader(string Filename, char splitCharacter = ';')
    {
		try
		{
	        string csvFile = File.ReadAllText(Filename);
	        string[] lines = csvFile.Split(new string[] { Environment.NewLine }, StringSplitOptions.None);
		
			
			content = new List<string[]>();
			
	        foreach (var line in lines)
	        {
	            content.Add ( line.Split(splitCharacter) );                
	        }		
		}
		catch
		{
			Debug.LogError("Could not load CSV-file:" + Filename );
		}
    }	
	
	
	/// <summary>
	/// Parses the number sequence.
	/// </summary>
	private List<string> ParseNumberSequence( string s )
	{
		char[] charArray = s.ToCharArray();
		bool startedNewNumber = false;
		List<string> numbers = new List<string>();
		string actualNumber = "";
		bool actualNumberNegativ = false;
		
		
		foreach( var c in charArray )
		{
			if( Char.IsDigit(c) && !startedNewNumber )
			{
				startedNewNumber = true;
				actualNumber += c;
			}
			else if(c == '-' && !startedNewNumber )
			{
				startedNewNumber = true;
				actualNumber += c;
			}
						
			else if(Char.IsDigit(c) || (c == '.' && startedNewNumber))
			{
				actualNumber += c;
			}
			
			else if( !Char.IsDigit(c) && startedNewNumber )
			{
				numbers.Add( actualNumber );
				startedNewNumber = false;
				actualNumber = "";
			}
		}
		
		return numbers;
	}
	
	
	/// <summary>
	/// Convert string to vector3
	/// </summary>
	private Vector3 StringToVector3( string s )
	{
		List<string> numbers = ParseNumberSequence( s );	
		if( numbers.Count != 3 ) throw new Exception("numbers.Count != 3");
		
		return new Vector3( (float)System.Convert.ToDouble(numbers[0], CultureInfo.GetCultureInfo("en-US").NumberFormat ),
                            (float)System.Convert.ToDouble(numbers[1], CultureInfo.GetCultureInfo("en-US").NumberFormat),
                            (float)System.Convert.ToDouble(numbers[2], CultureInfo.GetCultureInfo("en-US").NumberFormat));
		
		
	}
	
	/// <summary>
	/// Convert string to quaterinion
	/// </summary>
	private Quaternion StringToQuaterinion( string s )
	{
		List<string> numbers = ParseNumberSequence( s );
		
		if( numbers.Count != 4 ) throw new Exception("numbers.Count != 4");
		
		return new Quaternion( (float)System.Convert.ToDouble(numbers[0], CultureInfo.GetCultureInfo("en-US").NumberFormat ),
                               (float)System.Convert.ToDouble(numbers[1], CultureInfo.GetCultureInfo("en-US").NumberFormat),
                               (float)System.Convert.ToDouble(numbers[2], CultureInfo.GetCultureInfo("en-US").NumberFormat),
							   (float)System.Convert.ToDouble(numbers[3], CultureInfo.GetCultureInfo("en-US").NumberFormat));
				
	}
	
	
	
	
	/// <summary>
	/// Searches the csv file for the line, which contains the position and rotation information of a referenced prefab.
	/// If the loading of the file causes an exception, the default vaules for position and rotation are returned. 
	/// </summary>
	/// <param name='prefabName'>
	/// Prefab name.
	/// </param>
	/// <param name='position'>
	/// reference of a variable for position.
	/// </param>
	/// <param name='rotation'>
	/// reference of a variable for rotation.
	/// </param>
	public void SearchInformation( string prefabName, out Vector3 position, out Quaternion rotation )
	{
		position = new Vector3(0,0,0);
		rotation = new Quaternion(1,0,0,0);
		
		if(content != null)
		{		
			var a = from i in content
					where (i[0]).Trim() == prefabName
					select i;	
			
			if( a.Count() == 0 ) return;
			
			position =  StringToVector3 (a.First()[1]);
			rotation =  StringToQuaterinion (a.First()[2]);		
		}
	}
	
	
	
}