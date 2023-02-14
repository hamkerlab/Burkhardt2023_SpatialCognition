// Upgrade NOTE: replaced '_Object2World' with 'unity_ObjectToWorld'
// Upgrade NOTE: replaced '_World2Object' with 'unity_WorldToObject'

Shader "CylindricProjectionLit" {
	Properties {
		_Color("Main Color", Color) = (1,1,1,1)
		_MainTex("Base (RGB)", 2D) = "white" {}
		_FoVV ("Vertical Field of View", Float) = 60.0
		_F ("Far Sphere", Float) = 100.0
		_N ("Near Sphere", Float) = 0.3
		_Aspect("Angle Aspect", Float) = 1.77778
		_YValue("Y-Value", Float) = 0.5
	}

CGINCLUDE
#include "UnityCG.cginc"
#include "Lighting.cginc"
#include "AutoLight.cginc"
ENDCG

	SubShader {
			Tags{ "RenderType" = "Opaque" }
			LOD 200

		Pass{
			Tags{ "LightMode" = "ForwardBase" }
			CGPROGRAM
			#pragma vertex vert
			#pragma fragment frag
			#pragma multi_compile_fwdbase


			struct v2f {
				float4 pos : SV_POSITION;
				float2 uv : TEXCOORD0;
				float4 worldPos: TEXCOORD1;
				float3 n : TEXCOORD2;
				LIGHTING_COORDS(3,4)
			};
			float _F;
			float _N;
			float _FoVV;
			float _Aspect;
			float _YValue;

			v2f vert(appdata_base v)
			{
				v2f o;
				const float PI = 3.14159;
				float phi = _FoVV * PI / 360.0f;
				float theta = phi * _Aspect;

				o.pos = mul(UNITY_MATRIX_MV, v.vertex);

				float d = length(o.pos.xz);

				o.pos.xy /= d;

				float alpha = asin(o.pos.x);
				o.pos.x = alpha / theta;

				//float volumeHeight = abs(o.pos.z) * tan(phi) / d;

				//float volumeHeight = tan(phi);				// mid point
				float volumeHeight = tan(phi) * cos(theta * _YValue);
				o.pos.y /= -volumeHeight;
			
				o.pos.z = -sign(o.pos.z) * (d - _N) / (_F - _N);
				
				o.pos.w = 1.0f;	

				o.uv = v.texcoord;

				o.worldPos = normalize(mul(v.vertex, unity_ObjectToWorld));
				o.n = normalize(mul(float4(v.normal.xyz, 1.0f), unity_WorldToObject).xyz);;

				TRANSFER_VERTEX_TO_FRAGMENT(o);
				
				return o;
			}

			sampler2D _MainTex;
			fixed4 _Color;

			fixed4 frag(v2f i) : COLOR
			{
				fixed4 col = tex2D(_MainTex, i.uv) * _Color;

				half nl;
				if (_WorldSpaceLightPos0.w == 0.0)
					nl = max(0.0f, dot(i.n, normalize(_WorldSpaceLightPos0.xyz)));
				else
				{
					float3 vertexToLight = _WorldSpaceLightPos0.xyz - i.worldPos.xyz;
					nl = max(0.0f, dot(i.n, normalize(vertexToLight)));
				}

				half att = LIGHT_ATTENUATION(i);

				float3 ambient = UNITY_LIGHTMODEL_AMBIENT.rgb * _Color.rgb;
				float3 diffuse = nl * _LightColor0.rgb * _Color.rgb * att;

				col *= float4 ((diffuse + ambient) * 2.0f, 1.0f);

				return col;
			}

			ENDCG
		}
	Pass{
				Tags{ "LightMode" = "ForwardAdd" }
				Blend One One
				CGPROGRAM
#pragma vertex vert
#pragma fragment frag
#pragma multi_compile_fwdadd


				struct v2f {
				float4 pos : SV_POSITION;
				float2 uv : TEXCOORD0;
				float4 worldPos: TEXCOORD1;
				float3 n : TEXCOORD2;
				LIGHTING_COORDS(3, 4)
			};

			float _F;
			float _N;
			float _FoVV;
			float _Aspect;
			float _YValue;

			v2f vert(appdata_base v)
			{
				v2f o;
				const float PI = 3.14159;
				float phi = _FoVV * PI / 360.0f;
				float theta = phi * _Aspect;

				o.pos = mul(UNITY_MATRIX_MV, v.vertex);

				float d = length(o.pos.xz);

				o.pos.xy /= d;

				float alpha = asin(o.pos.x);
				o.pos.x = alpha / theta;

				//float volumeHeight = abs(o.pos.z) * tan(phi) / d;

				//float volumeHeight = tan(phi);				// mid point
				float volumeHeight = tan(phi) * cos(theta * _YValue);
				o.pos.y /= -volumeHeight;

				o.pos.z = -sign(o.pos.z) * (d - _N) / (_F - _N);

				o.pos.w = 1.0f;

				o.uv = v.texcoord;

				o.worldPos = normalize(mul(v.vertex, unity_ObjectToWorld));
				o.n = normalize(mul(float4(v.normal.xyz, 1.0f), unity_WorldToObject).xyz);;

				TRANSFER_VERTEX_TO_FRAGMENT(o);
				return o;
			}

			sampler2D _MainTex;
			fixed4 _Color;

			fixed4 frag(v2f i) : COLOR
			{
				fixed4 col = tex2D(_MainTex, i.uv) * _Color;

			half nl;
			if (_WorldSpaceLightPos0.w == 0.0)
				nl = max(0.0f, dot(i.n, normalize(_WorldSpaceLightPos0.xyz)));
			else
			{
				float3 vertexToLight = _WorldSpaceLightPos0.xyz - i.worldPos.xyz;
				nl = max(0.0f, dot(i.n, normalize(vertexToLight)));
			}

			half att = LIGHT_ATTENUATION(i);

			float3 diffuse = nl * _LightColor0.rgb * _Color.rgb * att;

			col *= float4 (diffuse * 2.0f, 1.0f);

			return col;
			}

				ENDCG
			}
	} 
	Fallback "Diffuse"
}
