// Upgrade NOTE: replaced 'mul(UNITY_MATRIX_MVP,*)' with 'UnityObjectToClipPos(*)'

Shader "TestTable" {
Properties {
	_Color("Main Color", Color) = (1,1,1,1)
	_MainTex("Base (RGB)", 2D) = "white" {}
}

CGINCLUDE
#include "UnityCG.cginc"
#include "Lighting.cginc"
#include "AutoLight.cginc"
ENDCG
SubShader {

		Tags{ 
			"IgnoreProjector" = "True"
			"RenderType" = "Opaque"
		}
		LOD 200

	Pass{
		Tags { "LightMode" = "ForwardBase" }
		CGPROGRAM
		#pragma vertex vert
		#pragma fragment frag
		#pragma exclude_renderers flash
		#pragma multi_compile_fwdbase nolightmap

		struct v2f {
			float4 pos : SV_POSITION;
			fixed4 diffuse : COLOR0;
			float2 uv : TEXCOORD0;
		};


		sampler2D _MainTex;
		float4 _MainTex_ST;
		fixed4 _Color;

		v2f vert(appdata_full v)
		{
			v2f o;

			o.pos = UnityObjectToClipPos(v.vertex);

			fixed ao = v.color.a;
			ao += 0.1; ao = saturate(ao * ao * ao);

			fixed3 color = v.color.rgb * _Color.rgb * ao;
			o.diffuse.rgb = color;
			o.diffuse.a = 1;
			o.diffuse *= 0.5;

			o.uv = TRANSFORM_TEX(v.texcoord, _MainTex);

			return o;
		}

		fixed4 frag(v2f i) : COLOR
		{
			fixed4 albedo = tex2D(_MainTex, i.uv);
			fixed alpha = albedo.a;

			half4 light = i.diffuse;
			light.rgb *= 2.0;

			return fixed4(albedo.rgb * light, 0.0);
		}

		ENDCG
	}
	/*
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

		v2f vert(appdata_base v)
		{
			v2f o;
			o.pos = v.vertex;
			o.pos = mul(UNITY_MATRIX_MVP, o.pos);

			o.uv = v.texcoord;
			o.worldPos = normalize(mul(v.vertex, _Object2World));
			o.n = normalize(mul(float4(v.normal.xyz, 1.0f), _World2Object).xyz);;

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
	*/
} 
Fallback "Diffuse"
}
