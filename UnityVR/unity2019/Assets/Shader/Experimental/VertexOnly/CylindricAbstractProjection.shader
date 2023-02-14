Shader "CylindricAbstractProjection" {
	Properties {
		_FoVV ("Vertical Field of View", Float) = 60.0
		_F ("Far Sphere", Float) = 100.0
		_N ("Near Sphere", Float) = 0.3
		_Aspect("Angle Aspect", Float) = 1.77778
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
				float phi = _FoVV * PI / 360.0f;
				float theta = phi * _Aspect;

				o.pos = mul(UNITY_MATRIX_MV, v.vertex);

				float dx = length(o.pos.xz);
				float dy = length(o.pos.yz);
				float d = length(o.pos.xyz);

				o.pos.x /= dx;
				o.pos.y /= dy;

				float alpha = asin(o.pos.x);
				float beta = asin(o.pos.y);

				o.pos.x = alpha / theta * cos(beta);
				o.pos.y = -beta / phi * cos(alpha); 
			
				o.pos.z = -sign(o.pos.z) * (d - _N) / (_F - _N);
				
				o.pos.w = 1.0f;	
				
				return o;
			}

			ENDCG
		}
	} 
	Fallback "Diffuse"
}
