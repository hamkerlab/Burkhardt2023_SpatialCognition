Shader "DividedByD" {
	Properties {
		_F ("Far Sphere", Float) = 100.0
		_N ("Near Sphere", Float) = 0.3
	}
	SubShader {
		Pass{

			CGPROGRAM
			// Upgrade NOTE: excluded shader from OpenGL ES 2.0 because it does not contain a surface program or both vertex and fragment programs.
			#pragma exclude_renderers gles

			#pragma vertex vert
			#include "UnityCG.cginc"

			struct v2f {
				float4 pos : POSITION;
			};

			float _F;
			float _N;

			v2f vert(appdata_base v)
			{
				v2f o;

				o.pos = mul(UNITY_MATRIX_MV, v.vertex);

				float d = length(o.pos.xyz);
			
				o.pos = mul(UNITY_MATRIX_P, o.pos);

				o.pos.z = sign(o.pos.z) * (d - _N) / (_F - _N) * d;
				
				o.pos.w = d;	
				
				return o;
			}

			ENDCG
		}
	} 
	Fallback "Diffuse"
}
