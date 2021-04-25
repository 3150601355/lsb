oFileBiao = null;
oFileLi = null;
oFileUnMix = null;

window.onload = function () {
	// ----------------------表图拖拽-----------------------------------------
	var oBoxBiao = document.getElementById('idBoxBiao');
	oBoxBiao.ondragover = function () {
		return false;
	};
	oBoxBiao.ondrop = function (ev) {
		oFileBiao = ev.dataTransfer.files[0];
		console.log("oFileBiao");
		console.log(oFileBiao);
		// 显示图片
		var reader = new FileReader();
		reader.onload = function (event) {
			document.getElementById('idImgBiao').src = event.target.result;
		};
		reader.readAsDataURL(oFileBiao);
		return false;
	};

	// --------------------------里图拖拽--------------------------------------
	var oBoxLi = document.getElementById('idBoxLi');
	oBoxLi.ondragover = function () {
		return false;
	};

	oBoxLi.ondrop = function (ev) {
		oFileLi = ev.dataTransfer.files[0];
		// 显示图片
		var reader = new FileReader();
		reader.onload = function (event) {
			document.getElementById('idImgLi').src = event.target.result;

			// 决定是否开始合成
			if (oFileBiao != null) {
				$("#idBtnMix").click();
			}
		};
		reader.readAsDataURL(oFileLi);
		return false;
	};

	// --------------------------混合图拖拽-------------------------------------
	var oBoxUnMix = document.getElementById('idBoxMix');
	oBoxUnMix.ondragover = function () {
		return false;
	};
	oBoxUnMix.ondrop = function (ev) {
		oFileUnMix = ev.dataTransfer.files[0];
		// 显示图片
		var reader = new FileReader();
		reader.onload = function (event) {
			document.getElementById('idImgMix').src = event.target.result;

			// 开始提取
			$("#idBtnUnMix").click();
		};
		reader.readAsDataURL(oFileUnMix);
		return false;
	};
};


$(function () {
	$('#idBtnMix').bind('click', function () {
		
		$.ajax({
			type: "POST",
			url: "/recv_img_biao",
			data: oFileBiao,
			processData: false,
			contentType: false
		}).done(function (o) {
		});

		$.ajax({
			type: "POST",
			url: "/recv_img_li",
			data: oFileLi,
			processData: false,
			contentType: false
		}).done(function (o) {
		});

		return false;
	});

	$('#idBtnUnMix').bind('click', function () {
		$.ajax({
			type: "POST",
			url: "/recv_img_unmix",
			data: oFileUnMix,
			processData: false,
			contentType: false
		}).done(function (o) {
		});
		return false;
	});

	setInterval(function () {
		loopUpdateSrc();
	}, 1000);
});

// 查询
function loopUpdateSrc() {
	$.getJSON("/get_data", function (result) {
		if (result.mix_src != "") {
			$("#idImgMix").attr("src", result.mix_src);
			$("#idAMix").attr("href", result.mix_src);
		}

		if (result.out_src != "") {
			$("#idImgLi").attr("src", result.out_src);
			$("#idALi").attr("href", result.out_src);
		}

	});
};