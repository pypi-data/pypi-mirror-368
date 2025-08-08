"""Test docker images."""

from imecilabt.gpulab.util.docker_image import DockerImageName


def test_docker_image_dockerhub_1():
    input = "debian:stable"
    actual = DockerImageName.from_str(input)
    assert str(actual) == input
    assert not actual.has_auth
    assert not actual.includes_registry
    assert actual.registry == "registry-1.docker.io"
    assert actual.image == "debian"
    assert actual.image_without_registry == "debian"
    assert actual.image_with_tag == "debian:stable"
    assert actual.tag == "stable"
    assert actual.user is None
    assert actual.password is None


def test_docker_image_dockerhub_2():
    input = "debian:latest"
    actual = DockerImageName.from_str(input)
    assert str(actual) == input
    assert not actual.has_auth
    assert not actual.includes_registry
    assert actual.registry == "registry-1.docker.io"
    assert actual.image == "debian"
    assert actual.image_without_registry == "debian"
    assert actual.image_with_tag == "debian:latest"
    assert actual.tag == "latest"
    assert actual.user is None
    assert actual.password is None


def test_docker_image_dockerhub_3():
    input = "debian"
    actual = DockerImageName.from_str(input)
    assert str(actual) == input + ":latest"
    assert not actual.has_auth
    assert not actual.includes_registry
    assert actual.registry == "registry-1.docker.io"
    assert actual.image == "debian"
    assert actual.image_without_registry == "debian"
    assert actual.image_with_tag == "debian:latest"
    assert actual.tag == "latest"
    assert actual.user is None
    assert actual.password is None


def test_docker_image_dockerhub_userpass_1():
    input = "foo:bar@debian:stable"
    actual = DockerImageName.from_str(input)
    assert str(actual) == input
    assert actual.has_auth
    assert not actual.includes_registry
    assert actual.registry == "registry-1.docker.io"
    assert actual.image == "debian"
    assert actual.image_without_registry == "debian"
    assert actual.image_with_tag == "debian:stable"
    assert actual.tag == "stable"
    assert actual.user == "foo"
    assert actual.password == "bar"


def test_docker_image_dockerhub_userpass_2():
    input = "foo:bar@debian:latest"
    actual = DockerImageName.from_str(input)
    assert str(actual) == input
    assert actual.has_auth
    assert not actual.includes_registry
    assert actual.registry == "registry-1.docker.io"
    assert actual.image == "debian"
    assert actual.image_without_registry == "debian"
    assert actual.image_with_tag == "debian:latest"
    assert actual.tag == "latest"
    assert actual.user == "foo"
    assert actual.password == "bar"


def test_docker_image_dockerhub_userpass_3():
    input = "foo:bar@debian"
    actual = DockerImageName.from_str(input)
    assert str(actual) == input + ":latest"
    assert actual.has_auth
    assert not actual.includes_registry
    assert actual.registry == "registry-1.docker.io"
    assert actual.image == "debian"
    assert actual.image_without_registry == "debian"
    assert actual.image_with_tag == "debian:latest"
    assert actual.tag == "latest"
    assert actual.user == "foo"
    assert actual.password == "bar"


def test_docker_image_private_reg_1():
    input = "example.com:4567/some/nested/name:v1"
    actual = DockerImageName.from_str(input)
    assert str(actual) == input
    assert not actual.has_auth
    assert actual.includes_registry
    assert actual.registry == "example.com:4567"
    assert actual.image == "example.com:4567/some/nested/name"
    assert actual.image_without_registry == "some/nested/name"
    assert actual.image_with_tag == "example.com:4567/some/nested/name:v1"
    assert actual.tag == "v1"
    assert actual.user is None
    assert actual.password is None


def test_docker_image_private_reg_2():
    input = "example.com:4567/some/nested/name:latest"
    actual = DockerImageName.from_str(input)
    assert str(actual) == input
    assert not actual.has_auth
    assert actual.includes_registry
    assert actual.registry == "example.com:4567"
    assert actual.image == "example.com:4567/some/nested/name"
    assert actual.image_without_registry == "some/nested/name"
    assert actual.image_with_tag == "example.com:4567/some/nested/name:latest"
    assert actual.tag == "latest"
    assert actual.user is None
    assert actual.password is None


def test_docker_image_private_reg_3():
    input = "example.com:4567/some/nested/name"
    actual = DockerImageName.from_str(input)
    assert str(actual) == input + ":latest"
    assert not actual.has_auth
    assert actual.includes_registry
    assert actual.registry == "example.com:4567"
    assert actual.image == "example.com:4567/some/nested/name"
    assert actual.image_without_registry == "some/nested/name"
    assert actual.image_with_tag == "example.com:4567/some/nested/name:latest"
    assert actual.tag == "latest"
    assert actual.user is None
    assert actual.password is None


def test_docker_image_private_reg_userpass_1():
    input = "foo:bar@example.com:4567/some/nested/name:v1"
    actual = DockerImageName.from_str(input)
    assert str(actual) == input
    assert actual.has_auth
    assert actual.includes_registry
    assert actual.registry == "example.com:4567"
    assert actual.image == "example.com:4567/some/nested/name"
    assert actual.image_without_registry == "some/nested/name"
    assert actual.image_with_tag == "example.com:4567/some/nested/name:v1"
    assert actual.tag == "v1"
    assert actual.user == "foo"
    assert actual.password == "bar"


def test_docker_image_private_reg_userpass_2():
    input = "foo:bar@example.com:4567/some/nested/name:latest"
    actual = DockerImageName.from_str(input)
    assert str(actual) == input
    assert actual.has_auth
    assert actual.includes_registry
    assert actual.registry == "example.com:4567"
    assert actual.image == "example.com:4567/some/nested/name"
    assert actual.image_without_registry == "some/nested/name"
    assert actual.image_with_tag == "example.com:4567/some/nested/name:latest"
    assert actual.tag == "latest"
    assert actual.user == "foo"
    assert actual.password == "bar"


def test_docker_image_private_reg_userpass_3():
    input = "foo:bar@example.com:4567/some/nested/name"
    actual = DockerImageName.from_str(input)
    assert str(actual) == input + ":latest"
    assert actual.has_auth
    assert actual.includes_registry
    assert actual.registry == "example.com:4567"
    assert actual.image == "example.com:4567/some/nested/name"
    assert actual.image_without_registry == "some/nested/name"
    assert actual.image_with_tag == "example.com:4567/some/nested/name:latest"
    assert actual.tag == "latest"
    assert actual.user == "foo"
    assert actual.password == "bar"
