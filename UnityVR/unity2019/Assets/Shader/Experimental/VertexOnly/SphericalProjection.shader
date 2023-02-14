Shader "SphericalProjection" {
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
				const float PI = 3.14159;

				// the standard Model-View-Transformation
				o.pos = mul(UNITY_MATRIX_MV, v.vertex);

				// here calculations for custom projection begin
				float PHI = _FoVV * PI / 360.0f;
				float THETA = PHI * _Aspect;

				float d = length(o.pos.xyz);
				float polar = asin(o.pos.y / d);
				float cp = cos(polar);

				o.pos.x = asin(o.pos.x / (cp * d)) * cp / THETA;
				o.pos.y = -polar / PHI;

				float z = (d - _N) / (_F - _N);

				if (z <= 0.0f)
				{
					o.pos.z = -0.0001f;
				}
				else
				{
					o.pos.z = -sign(o.pos.z) * z;
				}

				o.pos.w = 1.0f;

				return o;
			}

			ENDCG
		}
	} 
	Fallback "Diffuse"
}
