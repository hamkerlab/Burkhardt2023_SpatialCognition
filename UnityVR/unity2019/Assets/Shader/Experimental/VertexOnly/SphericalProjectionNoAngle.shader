// Upgrade NOTE: replaced 'mul(UNITY_MATRIX_MVP,*)' with 'UnityObjectToClipPos(*)'

Shader "SphericalProjectionNA" {
	Properties {
		_FoVV ("Vertical Field of View", Float) = 60.0
		_F ("Far Sphere", Float) = 100.0
		_N ("Near Sphere", Float) = 0.3
		_Aspect("Angle Aspect", Float) = 1.52488
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
			float _FoVV;
			float _Aspect;

			v2f vert(appdata_base v)
			{
				v2f o;
				v2f p;

				o.pos = mul(UNITY_MATRIX_MV, v.vertex);
				p.pos = UnityObjectToClipPos(v.vertex);

				float d = length(o.pos.xyz);
				
				o.pos.x = o.pos.x / d;
				//o.pos.x = 0.4f * sign(o.pos.x);
				o.pos.y = -o.pos.y / d;
			
				o.pos.z = -sign(o.pos.z) * (d - _N) / (_F - _N);

				o.pos.w = 1.0f;	
				
				return o;
			}

			ENDCG
		}
	} 
	Fallback "Diffuse"
}
